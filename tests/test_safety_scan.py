from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "safety_scan.py"
SPEC = importlib.util.spec_from_file_location("safety_scan", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
safety_scan = importlib.util.module_from_spec(SPEC)
sys.modules["safety_scan"] = safety_scan
SPEC.loader.exec_module(safety_scan)


class SafetyScanTests(unittest.TestCase):
    def test_current_runtime_code_passes_scan(self) -> None:
        findings = safety_scan.scan_paths([safety_scan.REPO_ROOT / "src"])

        self.assertEqual(findings, [])

    def test_detects_pyautogui_click_call(self) -> None:
        findings = _scan_source(
            """
            import pyautogui

            pyautogui.click(10, 10)
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("pyautogui.click", findings[0].detail)

    def test_detects_pyautogui_alias_move_to_call(self) -> None:
        findings = _scan_source(
            """
            import pyautogui as pag

            pag.moveTo(10, 10)
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("pyautogui.moveTo", findings[0].detail)

    def test_detects_keyboard_press_from_import(self) -> None:
        findings = _scan_source(
            """
            from keyboard import press

            press("enter")
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("keyboard.press", findings[0].detail)

    def test_detects_mouse_click_alias(self) -> None:
        findings = _scan_source(
            """
            import mouse as desktop_mouse

            desktop_mouse.click()
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("mouse.click", findings[0].detail)

    def test_detects_pynput_mouse_controller_actuation(self) -> None:
        findings = _scan_source(
            """
            from pynput.mouse import Controller

            mouse = Controller()
            mouse.click(None)
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("mouse.click", findings[0].detail)
        self.assertIn("pynput.mouse.Controller", findings[0].detail)

    def test_detects_pynput_keyboard_controller_position_or_press(self) -> None:
        findings = _scan_source(
            """
            from pynput import keyboard

            keys = keyboard.Controller()
            keys.press("a")
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("keys.press", findings[0].detail)
        self.assertIn("pynput.keyboard.Controller", findings[0].detail)

    def test_detects_inline_pynput_controller_actuation(self) -> None:
        findings = _scan_source(
            """
            import pynput.mouse

            pynput.mouse.Controller().click(None)
            """
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("pynput.mouse.Controller().click", findings[0].detail)

    def test_scan_focuses_on_requested_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            docs_dir = root / "docs"
            tests_dir = root / "tests"
            src_dir.mkdir()
            docs_dir.mkdir()
            tests_dir.mkdir()
            (src_dir / "safe.py").write_text("value = 1\n", encoding="utf-8")
            (docs_dir / "example.py").write_text("import pyautogui\npyautogui.click()\n", encoding="utf-8")
            (tests_dir / "example_test.py").write_text("import mouse\nmouse.click()\n", encoding="utf-8")

            findings = safety_scan.scan_paths([src_dir])

        self.assertEqual(findings, [])


def _scan_source(source: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "runtime_sample.py"
        path.write_text(_dedent(source), encoding="utf-8")
        return safety_scan.scan_paths([path])


def _dedent(source: str) -> str:
    lines = source.strip("\n").splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    return "\n".join(line[indent:] for line in lines) + "\n"
