"""Normalized visible-element schema for read-only desktop grounding.

The observer schema is intentionally narrow: it records what the system can see
without implying that any element is safe to click, type into, or otherwise
actuate. Downstream planners and readiness checks must treat these records as
read-only grounding only.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


VISIBLE_ELEMENT_SOURCES = {"ocr", "ui_tree", "manual"}
VISIBLE_ELEMENT_RISK_HINTS = {"normal", "high_risk", "unknown"}

HIGH_RISK_LABELS = [
    "send",
    "submit",
    "delete",
    "remove",
    "pay",
    "purchase",
    "buy",
    "confirm",
    "password",
    "login",
    "sign in",
    "log in",
    "发送",
    "删除",
    "支付",
    "购买",
    "确认",
    "密码",
    "登录",
]


@dataclass(frozen=True)
class BBox:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class VisibleElement:
    """A normalized read-only UI element visible in one observation.

    `bbox` and `center` use screen coordinates. `source` identifies the
    read-only grounding source, while `risk_hint` is a label-level hint only and
    never grants permission to execute desktop input.
    """

    id: str
    label: str
    text: str
    role: str
    bbox: BBox
    center: Point
    confidence: float
    source: str
    risk_hint: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def visible_element_from_text_box(
    text_box: dict[str, Any],
    index: int,
    screen: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any] | None:
    """Convert one OCR text box into the stable VisibleElement schema."""

    return normalize_visible_element(
        {
            "id": f"element_{index + 1:04d}",
            "source": "ocr",
            "role": "text",
            "label": text_box.get("text"),
            "text": text_box.get("text"),
            "bbox": text_box.get("bbox"),
            "confidence": text_box.get("confidence", 0.0),
        },
        index=index,
        screen=screen,
        timestamp=timestamp,
    )


def visible_element_from_ui_tree_node(
    node: dict[str, Any],
    index: int,
    screen: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any] | None:
    """Convert one fixture-provided UI tree node into VisibleElement.

    This adapter is read-only and intentionally accepts plain dictionaries. It
    does not call platform accessibility, automation, mouse, or keyboard APIs.
    Hidden or disabled nodes are retained only as low-confidence grounding, so
    planners can show/debug them without treating them as safe targets.
    """

    if not isinstance(node, dict):
        return None

    visible = _truthy_ui_tree_flag(node.get("is_visible"), default=True)
    enabled = _truthy_ui_tree_flag(node.get("is_enabled"), default=True)
    actionable = visible and enabled
    confidence = normalize_confidence(node.get("confidence", 1.0 if actionable else 0.0))
    if not actionable:
        confidence = 0.0

    return normalize_visible_element(
        {
            "id": _ui_tree_node_id(node, index),
            "source": "ui_tree",
            "role": _ui_tree_role(node),
            "label": _ui_tree_text(node, ["name", "label", "title", "value", "text", "automation_id"]),
            "text": _ui_tree_text(node, ["text", "name", "label", "title", "value", "automation_id"]),
            "bbox": _ui_tree_bbox(node),
            "confidence": confidence,
            "risk_hint": node.get("risk_hint") if actionable else "unknown",
        },
        index=index,
        screen=screen,
        timestamp=timestamp or node.get("timestamp"),
    )


def visible_elements_from_ui_tree(
    ui_tree: Any,
    screen: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize fixture-friendly UI tree input into VisibleElement records."""

    elements: list[dict[str, Any]] = []
    for node in _flatten_ui_tree_nodes(ui_tree):
        element = visible_element_from_ui_tree_node(
            node,
            index=len(elements),
            screen=screen,
            timestamp=timestamp,
        )
        if element is not None:
            elements.append(element)

    return normalize_visible_elements(elements, screen=screen, timestamp=timestamp)


def normalize_visible_elements(
    elements: Any,
    screen: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize a list of candidate element dictionaries and enforce IDs."""

    if not isinstance(elements, list):
        return []

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_element in enumerate(elements):
        element = normalize_visible_element(
            raw_element,
            index=index,
            screen=screen,
            timestamp=timestamp,
        )
        if element is None:
            continue

        element["id"] = _unique_element_id(element["id"], seen_ids)
        seen_ids.add(element["id"])
        normalized.append(element)

    return normalized


def normalize_visible_element(
    element: Any,
    index: int = 0,
    screen: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any] | None:
    """Return a valid VisibleElement dictionary, or None when unsafe to ground."""

    if not isinstance(element, dict):
        return None

    bbox = _normalized_bbox(element.get("bbox"), screen)
    if bbox is None:
        return None

    label = normalize_label_text(_first_text(element, ["label", "name", "title", "value", "text"]))
    text = normalize_label_text(_first_text(element, ["text", "label", "name", "title", "value"]))
    if not label and not text:
        return None

    visible_element = VisibleElement(
        id=_normalized_element_id(element.get("id"), index),
        label=label,
        text=text,
        role=_normalized_role(_first_text(element, ["role", "type", "kind"]) or "unknown"),
        bbox=BBox(**bbox),
        center=Point(**_center_from_bbox(bbox)),
        confidence=normalize_confidence(element.get("confidence", 0.0)),
        source=_normalized_source(element.get("source")),
        risk_hint=_risk_hint(element.get("risk_hint"), label, text),
        timestamp=_normalized_timestamp(timestamp or element.get("timestamp")),
    )

    payload = visible_element.to_dict()
    if visible_element_schema_errors(payload, screen=screen):
        return None

    return payload


def visible_element_schema_errors(
    element: Any,
    screen: dict[str, Any] | None = None,
) -> list[str]:
    """Return schema validation errors for a normalized VisibleElement payload."""

    if not isinstance(element, dict):
        return ["visible element must be an object"]

    errors: list[str] = []
    required_fields = {
        "id",
        "label",
        "text",
        "role",
        "bbox",
        "center",
        "confidence",
        "source",
        "risk_hint",
        "timestamp",
    }

    missing = sorted(field for field in required_fields if field not in element)
    errors.extend(f"missing field: {field}" for field in missing)
    if missing:
        return errors

    if not _non_empty_string(element.get("id")):
        errors.append("id must be a non-empty string")

    label = element.get("label")
    text = element.get("text")
    if not isinstance(label, str) or label != normalize_label_text(label):
        errors.append("label must be normalized text")
    if not isinstance(text, str) or text != normalize_label_text(text):
        errors.append("text must be normalized text")
    if not str(label or text).strip():
        errors.append("label or text must be non-empty")

    if not _non_empty_string(element.get("role")):
        errors.append("role must be a non-empty string")

    bbox = _strict_int_bbox(element.get("bbox"))
    if bbox is None:
        errors.append("bbox must contain integer x, y, width, and height")
    elif _normalized_bbox(bbox, screen) is None:
        errors.append("bbox must be positive and inside screen bounds when provided")

    center = _strict_int_point(element.get("center"))
    if center is None:
        errors.append("center must contain integer x and y")
    elif bbox is not None and center != _center_from_bbox(bbox):
        errors.append("center must match bbox center")

    confidence = _finite_float(element.get("confidence"))
    if confidence is None or confidence < 0.0 or confidence > 1.0:
        errors.append("confidence must be between 0 and 1")

    if element.get("source") not in VISIBLE_ELEMENT_SOURCES:
        errors.append("source must be one of ocr, ui_tree, or manual")

    if element.get("risk_hint") not in VISIBLE_ELEMENT_RISK_HINTS:
        errors.append("risk_hint must be normal, high_risk, or unknown")

    if _parse_timestamp(element.get("timestamp")) is None:
        errors.append("timestamp must be ISO8601")

    return errors


def is_valid_visible_element(
    element: Any,
    screen: dict[str, Any] | None = None,
) -> bool:
    return not visible_element_schema_errors(element, screen=screen)


def normalize_label_text(value: Any) -> str:
    """Trim, lowercase, remove punctuation/symbols, and collapse whitespace."""

    pieces: list[str] = []
    for character in str(value or "").strip().casefold():
        if character.isalnum():
            pieces.append(character)
        elif character.isspace():
            pieces.append(" ")
        else:
            pieces.append(" ")

    return " ".join("".join(pieces).split())


def normalize_confidence(value: Any) -> float:
    number = _finite_float(value)
    if number is None:
        return 0.0

    if number > 1.0:
        number = number / 100.0

    return max(0.0, min(float(number), 1.0))


def visible_element_schema_metadata() -> dict[str, Any]:
    return {
        "fields": [
            "id",
            "label",
            "text",
            "role",
            "bbox",
            "center",
            "confidence",
            "source",
            "risk_hint",
            "timestamp",
        ],
        "sources": sorted(VISIBLE_ELEMENT_SOURCES),
        "risk_hints": sorted(VISIBLE_ELEMENT_RISK_HINTS),
        "label_normalization": "trim, lowercase, remove punctuation/symbols, collapse whitespace",
    }


def _normalized_bbox(value: Any, screen: dict[str, Any] | None) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None

    try:
        bbox = {
            "x": int(float(value["x"])),
            "y": int(float(value["y"])),
            "width": int(float(value["width"])),
            "height": int(float(value["height"])),
        }
    except (KeyError, TypeError, ValueError):
        return None

    if bbox["x"] < 0 or bbox["y"] < 0 or bbox["width"] <= 0 or bbox["height"] <= 0:
        return None

    bounds = _screen_bounds(screen)
    if bounds is not None:
        screen_width, screen_height = bounds
        if bbox["x"] + bbox["width"] > screen_width or bbox["y"] + bbox["height"] > screen_height:
            return None

    return bbox


def _strict_int_bbox(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None

    bbox: dict[str, int] = {}
    for key in ["x", "y", "width", "height"]:
        number = value.get(key)
        if not isinstance(number, int) or isinstance(number, bool):
            return None
        bbox[key] = number

    return bbox


def _strict_int_point(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None

    point: dict[str, int] = {}
    for key in ["x", "y"]:
        number = value.get(key)
        if not isinstance(number, int) or isinstance(number, bool):
            return None
        point[key] = number

    return point


def _center_from_bbox(bbox: dict[str, int]) -> dict[str, int]:
    return {
        "x": round(bbox["x"] + bbox["width"] / 2),
        "y": round(bbox["y"] + bbox["height"] / 2),
    }


def _screen_bounds(screen: dict[str, Any] | None) -> tuple[int, int] | None:
    if not isinstance(screen, dict):
        return None

    try:
        width = int(float(screen["width"]))
        height = int(float(screen["height"]))
    except (KeyError, TypeError, ValueError):
        return None

    if width <= 0 or height <= 0:
        return None

    return width, height


def _first_text(element: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = element.get(key)
        if value is None:
            continue

        text = str(value).strip()
        if text:
            return text

    return ""


def _flatten_ui_tree_nodes(value: Any) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    if isinstance(value, list):
        for item in value:
            nodes.extend(_flatten_ui_tree_nodes(item))
        return nodes

    if not isinstance(value, dict):
        return nodes

    nodes.append(value)
    for key in ["children", "items", "nodes", "elements"]:
        children = value.get(key)
        if isinstance(children, list):
            for child in children:
                nodes.extend(_flatten_ui_tree_nodes(child))

    return nodes


def _ui_tree_node_id(node: dict[str, Any], index: int) -> str:
    for key in ["id", "automation_id", "runtime_id", "name", "text"]:
        value = node.get(key)
        if value:
            return f"ui_tree_{value}"

    return f"ui_tree_{index + 1:04d}"


def _ui_tree_role(node: dict[str, Any]) -> str:
    return _ui_tree_text(node, ["control_type", "role", "type", "kind"]) or "unknown"


def _ui_tree_text(node: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = node.get(key)
        if value is None:
            continue

        text = str(value).strip()
        if text:
            return text

    return ""


def _ui_tree_bbox(node: dict[str, Any]) -> Any:
    for key in ["bounding_rectangle", "bbox", "bounds", "rect"]:
        value = node.get(key)
        if isinstance(value, dict):
            return value

    return None


def _truthy_ui_tree_flag(value: Any, default: bool) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "visible", "enabled"}:
            return True
        if normalized in {"false", "0", "no", "n", "hidden", "disabled"}:
            return False

    return bool(value)


def _normalized_element_id(value: Any, index: int) -> str:
    raw_id = str(value or "").strip()
    if not raw_id:
        return f"element_{index + 1:04d}"

    safe_id = "".join(character if character.isalnum() or character in {"_", "-"} else "_" for character in raw_id)
    return safe_id.strip("_") or f"element_{index + 1:04d}"


def _unique_element_id(element_id: str, seen_ids: set[str]) -> str:
    if element_id not in seen_ids:
        return element_id

    suffix = 2
    while f"{element_id}_{suffix}" in seen_ids:
        suffix += 1

    return f"{element_id}_{suffix}"


def _normalized_role(value: Any) -> str:
    role = normalize_label_text(value).replace(" ", "_")
    return role or "unknown"


def _normalized_source(value: Any) -> str:
    source = _normalized_role(value)
    if source in VISIBLE_ELEMENT_SOURCES:
        return source
    if source in {"accessibility", "uia", "ui_automation", "dom"}:
        return "ui_tree"
    if source in {"demo", "fixture", "test", "mock", "manual"}:
        return "manual"
    if source == "ocr":
        return "ocr"
    return "manual"


def _risk_hint(raw_hint: Any, label: str, text: str) -> str:
    explicit = normalize_label_text(raw_hint).replace(" ", "_")
    if explicit in {"high", "high_risk"}:
        return "high_risk"
    if explicit in {"normal", "none", "low"}:
        return "normal"
    if explicit == "unknown":
        return "unknown"

    haystack = " ".join(value for value in [label, text] if value)
    if not haystack:
        return "unknown"

    for high_risk_label in HIGH_RISK_LABELS:
        risk_label = normalize_label_text(high_risk_label)
        if risk_label and risk_label in haystack:
            return "high_risk"

    return "normal"


def _normalized_timestamp(value: Any) -> str:
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
