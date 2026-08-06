import json
from importlib.resources import files

import jsonschema

from .exceptions import ParseError


_SCHEMA: dict | None = None


def load_schema() -> dict:
    """Load and cache the arglite JSON schema."""
    global _SCHEMA
    if _SCHEMA is None:
        schema_text = files("arglite").joinpath("schema.json").read_text(encoding="utf-8")
        _SCHEMA = json.loads(schema_text)
    return _SCHEMA


def validate_config(config: dict, path: str) -> None:
    """Validate a loaded YAML config dict against the arglite schema.

    The schema is lenient: unknown top-level keys and unknown flag fields are
    allowed. This lets users experiment and extend their configs without
    breaking validation.
    """
    try:
        jsonschema.validate(instance=config, schema=load_schema())
    except jsonschema.ValidationError as exc:
        raise ParseError(
            f"ERROR: Invalid YAML config '{path}': {exc.message}"
        ) from exc
