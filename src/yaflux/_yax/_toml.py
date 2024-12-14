import re
from typing import Any


def _escape_toml_string(s: str) -> str:
    """Escape a string for TOML formatting."""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _format_toml_value(value: Any) -> str:
    """Format a Python value as a TOML value."""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Use basic strings for simple cases, literal strings for complex ones
        if re.match(r"^[a-zA-Z0-9_.-]+$", value):
            return value
        return f'"{_escape_toml_string(value)}"'
    elif isinstance(value, (list, tuple)):
        items = [_format_toml_value(item) for item in value]
        return f"[{', '.join(items)}]"
    elif isinstance(value, dict):
        items = [f"{k} = {_format_toml_value(v)}" for k, v in value.items()]
        return f"{{ {', '.join(items)} }}"
    else:
        return f'"{_escape_toml_string(str(value))}"'


def _format_toml_section(data: dict, prefix: str = "") -> list[str]:
    """Format a dictionary as TOML section(s)."""
    lines = []
    simple_pairs = []
    sections = []

    for key, value in data.items():
        if isinstance(value, dict):
            if prefix:
                section_name = f"{prefix}.{key}"
            else:
                section_name = key
            sections.extend(["", f"[{section_name}]", *_format_toml_section(value)])
        else:
            simple_pairs.append(f"{key} = {_format_toml_value(value)}")

    if simple_pairs:
        lines.extend(simple_pairs)
    lines.extend(sections)
    return lines
