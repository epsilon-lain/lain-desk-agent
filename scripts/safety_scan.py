from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCAN_ROOTS = [REPO_ROOT / "src"]

FORBIDDEN_MODULE_ATTRS = {
    "pyautogui": {
        "click",
        "doubleClick",
        "dragTo",
        "hotkey",
        "keyDown",
        "keyUp",
        "move",
        "moveTo",
        "mouseDown",
        "mouseUp",
        "press",
        "scroll",
        "typewrite",
        "write",
    },
    "keyboard": {
        "hotkey",
        "press",
        "release",
        "send",
        "type",
        "write",
    },
    "mouse": {
        "click",
        "drag",
        "move",
        "press",
        "release",
        "scroll",
        "wheel",
    },
}

PYNPUT_CONTROLLER_ATTRS = {
    "click",
    "move",
    "press",
    "release",
    "scroll",
    "tap",
    "type",
}

PYNPUT_CONTROLLER_MODULES = {
    "pynput.mouse": "mouse",
    "pynput.keyboard": "keyboard",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    column: int
    rule: str
    detail: str

    def format(self) -> str:
        try:
            relative = self.path.relative_to(REPO_ROOT)
        except ValueError:
            relative = self.path
        return f"{relative}:{self.line}:{self.column + 1}: {self.rule}: {self.detail}"


class SafetyScanVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[Finding] = []
        self.module_aliases: dict[str, str] = {}
        self.forbidden_call_names: dict[str, str] = {}
        self.pynput_controller_factories: dict[str, str] = {}
        self.pynput_controller_aliases: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_name = alias.name
            local_name = alias.asname or module_name.split(".", 1)[0]
            if module_name in FORBIDDEN_MODULE_ATTRS:
                self.module_aliases[local_name] = module_name
            elif module_name in PYNPUT_CONTROLLER_MODULES:
                self.module_aliases[local_name] = module_name
            elif module_name == "pynput":
                self.module_aliases[local_name] = module_name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name = node.module or ""
        for alias in node.names:
            imported_name = alias.name
            local_name = alias.asname or imported_name
            if imported_name == "*":
                if module_name in FORBIDDEN_MODULE_ATTRS or module_name in PYNPUT_CONTROLLER_MODULES:
                    self._add(node, "forbidden desktop control wildcard import", f"from {module_name} import *")
                continue
            if module_name in FORBIDDEN_MODULE_ATTRS and imported_name in FORBIDDEN_MODULE_ATTRS[module_name]:
                self.forbidden_call_names[local_name] = f"{module_name}.{imported_name}"
            elif module_name in PYNPUT_CONTROLLER_MODULES and imported_name == "Controller":
                controller_kind = PYNPUT_CONTROLLER_MODULES[module_name]
                self.pynput_controller_factories[local_name] = f"pynput.{controller_kind}.Controller"
            elif module_name == "pynput" and imported_name in {"mouse", "keyboard"}:
                self.module_aliases[local_name] = f"pynput.{imported_name}"
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._track_controller_assignment(node.targets, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._track_controller_assignment([node.target], node.value)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        direct_call = self._direct_call_detail(node.func)
        if direct_call:
            self._add(node, "forbidden desktop actuation call", direct_call)

        controller_call = self._pynput_controller_call_detail(node.func)
        if controller_call:
            self._add(node, "forbidden pynput controller actuation", controller_call)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if (
            node.attr == "position"
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and node.value.id in self.pynput_controller_aliases
        ):
            detail = f"{node.value.id}.position assignment via {self.pynput_controller_aliases[node.value.id]}"
            self._add(node, "forbidden pynput controller actuation", detail)
        self.generic_visit(node)

    def _track_controller_assignment(self, targets: list[ast.expr], value: ast.expr) -> None:
        factory = self._pynput_controller_factory_detail(value)
        if not factory:
            return
        for target in targets:
            if isinstance(target, ast.Name):
                self.pynput_controller_aliases[target.id] = factory

    def _direct_call_detail(self, func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return self.forbidden_call_names.get(func.id, "")
        if not isinstance(func, ast.Attribute):
            return ""

        owner = func.value
        if isinstance(owner, ast.Name):
            module_name = self.module_aliases.get(owner.id)
            if module_name in FORBIDDEN_MODULE_ATTRS and func.attr in FORBIDDEN_MODULE_ATTRS[module_name]:
                return f"{module_name}.{func.attr}"

        return ""

    def _pynput_controller_factory_detail(self, value: ast.expr) -> str:
        if not isinstance(value, ast.Call):
            return ""
        if isinstance(value.func, ast.Name):
            return self.pynput_controller_factories.get(value.func.id, "")

        chain = _attribute_chain(value.func)
        if chain.endswith(".Controller"):
            for module_name, kind in PYNPUT_CONTROLLER_MODULES.items():
                if chain == f"{module_name}.Controller":
                    return f"pynput.{kind}.Controller"

        if isinstance(value.func, ast.Attribute) and value.func.attr == "Controller":
            owner = value.func.value
            if isinstance(owner, ast.Name):
                module_name = self.module_aliases.get(owner.id, "")
                if module_name in PYNPUT_CONTROLLER_MODULES:
                    kind = PYNPUT_CONTROLLER_MODULES[module_name]
                    return f"pynput.{kind}.Controller"
            if isinstance(owner, ast.Attribute):
                owner_chain = _attribute_chain(owner)
                if owner_chain in PYNPUT_CONTROLLER_MODULES:
                    kind = PYNPUT_CONTROLLER_MODULES[owner_chain]
                    return f"pynput.{kind}.Controller"
        return ""

    def _pynput_controller_call_detail(self, func: ast.expr) -> str:
        if not isinstance(func, ast.Attribute):
            return ""
        if isinstance(func.value, ast.Call):
            factory = self._pynput_controller_factory_detail(func.value)
            if factory and func.attr in PYNPUT_CONTROLLER_ATTRS:
                return f"{factory}().{func.attr}"
            return ""
        if not isinstance(func.value, ast.Name):
            return ""
        owner_name = func.value.id
        if owner_name in self.pynput_controller_aliases and func.attr in PYNPUT_CONTROLLER_ATTRS:
            return f"{owner_name}.{func.attr} via {self.pynput_controller_aliases[owner_name]}"
        return ""

    def _add(self, node: ast.AST, rule: str, detail: str) -> None:
        self.findings.append(
            Finding(
                path=self.path,
                line=getattr(node, "lineno", 0),
                column=getattr(node, "col_offset", 0),
                rule=rule,
                detail=detail,
            )
        )


def scan_paths(paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in _python_files(paths):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            findings.append(
                Finding(
                    path=path,
                    line=exc.lineno or 0,
                    column=exc.offset or 0,
                    rule="python parse error",
                    detail=exc.msg,
                )
            )
            continue
        visitor = SafetyScanVisitor(path)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan runtime code for forbidden desktop actuation calls.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=DEFAULT_SCAN_ROOTS,
        help="Runtime paths to scan. Defaults to src/.",
    )
    args = parser.parse_args(argv)

    findings = scan_paths(_resolve_scan_paths(args.paths))
    if findings:
        print("Safety scan failed: forbidden runtime desktop actuation was found.")
        for finding in findings:
            print(finding.format())
        return 1

    print("Safety scan passed: no forbidden runtime desktop actuation calls found.")
    return 0


def _resolve_scan_paths(paths: Iterable[Path]) -> list[Path]:
    resolved = []
    for path in paths:
        if path.is_absolute():
            resolved.append(path)
        else:
            resolved.append(REPO_ROOT / path)
    return resolved


def _python_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            yield path
        elif path.is_dir():
            yield from sorted(path.rglob("*.py"))


def _attribute_chain(node: ast.AST) -> str:
    parts: list[str] = []
    current: ast.AST | None = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    parts.reverse()
    return ".".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
