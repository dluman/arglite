from typing import Optional

from .exceptions import ParseError
from .flag import Flag


def tokenize(argv: list[str], flags: dict[str, Flag]) -> dict[str, list[str]]:
    """Turn argv into a mapping of canonical flag names to raw values.

    The caller supplies the declared flags so that the tokenizer knows which
    flags expect a value (and should consume the next token even if it looks
    like a flag, e.g. a negative number) and which are boolean flags.
    """
    result: dict[str, list[str]] = {}
    i = 0
    while i < len(argv):
        arg = argv[i]
        raw_name, inline_value = _split_flag(arg)

        if raw_name is None:
            raise ParseError(
                f"ERROR: Unexpected positional argument: {arg!r}"
            )

        name = _canonical(raw_name, flags)
        flag = flags.get(name)

        if inline_value is not None:
            result.setdefault(name, []).append(inline_value)
            i += 1
            continue

        if flag is not None and not flag.expects_value:
            # Boolean flag used without a value.
            result.setdefault(name, [])
            i += 1
            continue

        # Flag expects a value; consume the next token.
        if i + 1 >= len(argv):
            raise ParseError(
                f"ERROR: --{name} was provided without a value"
            )
        result.setdefault(name, []).append(argv[i + 1])
        i += 2

    return result


def _split_flag(arg: str) -> tuple[Optional[str], Optional[str]]:
    """Parse a single argv token into (name, value) or (name, None).

    Returns (None, None) for tokens that are not flags.
    """
    if arg.startswith("--"):
        body = arg[2:]
        if not body:
            raise ParseError("ERROR: Empty flag name '--'")
        if "=" in body:
            name, value = body.split("=", 1)
            return name, value
        return body, None

    if arg.startswith("-") and len(arg) > 1:
        body = arg[1:]
        if "=" in body:
            name, value = body.split("=", 1)
            return name, value
        return body, None

    return None, None


def _canonical(name: str, flags: dict[str, Flag]) -> str:
    """Map a parsed flag name to its canonical declared name."""
    if name in flags:
        return name
    for flag in flags.values():
        if flag.short == name:
            return flag.name
    return name
