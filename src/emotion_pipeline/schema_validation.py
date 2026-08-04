"""Executable validation against the repository's JSON Schema contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .contracts import ContractError


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def validate_schema(schema_name: str, value: Any) -> list[str]:
    """Return readable validation errors for a named repository schema."""

    schema_path = SCHEMA_DIR / f"{schema_name}.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "$"
        messages.append(f"{location}: {error.message}")
    return messages


def assert_schema(schema_name: str, value: Any) -> None:
    """Raise a contract error when a value violates a repository schema."""

    errors = validate_schema(schema_name, value)
    if errors:
        raise ContractError(f"{schema_name} schema validation failed: {'; '.join(errors)}")

