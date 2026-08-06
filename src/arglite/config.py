import os
from typing import Any, Callable

import yaml

from .exceptions import ParseError
from .flag import Flag
from .validate import validate_config


TYPE_MAP: dict[str, Callable[[str], Any]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def load_yaml(path: str, optional: bool = False) -> dict[str, Flag]:
    """Load flag declarations from a YAML file.

    If ``optional`` is True and the file does not exist, an empty dict is
    returned. Otherwise, a missing file raises ParseError.
    """
    if not os.path.exists(path):
        if optional:
            return {}
        raise ParseError(f"ERROR: Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise ParseError(f"ERROR: Could not parse YAML config: {exc}") from exc

    validate_config(data, path)

    flags = data.get("flags", {})
    if not isinstance(flags, dict):
        raise ParseError("ERROR: YAML config 'flags' must be a mapping")

    return {name: _build_flag(name, spec) for name, spec in flags.items()}


def _build_flag(name: str, spec: Any) -> Flag:
    """Build a Flag object from a YAML specification."""
    if spec is None:
        spec = {}
    if not isinstance(spec, dict):
        raise ParseError(
            f"ERROR: Flag '{name}' specification must be a mapping"
        )

    short = spec.get("short")
    if short is not None and not isinstance(short, str):
        raise ParseError(
            f"ERROR: Flag '{name}' short must be a single character string"
        )

    type_name = spec.get("type")
    flag_type = None
    if type_name is not None:
        if not isinstance(type_name, str) or type_name not in TYPE_MAP:
            raise ParseError(
                f"ERROR: Flag '{name}' has unknown type: {type_name!r}"
            )
        flag_type = TYPE_MAP[type_name]

    action = spec.get("action")
    is_flag = False
    if action is not None:
        if action not in ("store_true", "store_false"):
            raise ParseError(
                f"ERROR: Flag '{name}' has unknown action: {action!r}"
            )
        is_flag = True
        flag_type = bool

    default = spec.get("default")
    if is_flag and default is None:
        default = action == "store_false"

    required = spec.get("required", False)
    if not isinstance(required, bool):
        raise ParseError(
            f"ERROR: Flag '{name}' required must be true or false"
        )

    help_text = spec.get("help")
    if help_text is not None and not isinstance(help_text, str):
        raise ParseError(
            f"ERROR: Flag '{name}' help must be a string"
        )

    choices = spec.get("choices")
    if choices is not None and not isinstance(choices, list):
        raise ParseError(
            f"ERROR: Flag '{name}' choices must be a list"
        )

    return Flag(
        name=name,
        short=short,
        required=required,
        default=default,
        type=flag_type,
        is_flag=is_flag,
        help=help_text,
        choices=choices,
    )
