from ast import literal_eval
from typing import Any, Callable, Optional

from .exceptions import ParseError


class Flag:
    """Descriptor for a declared CLI flag."""

    def __init__(
        self,
        name: str,
        short: Optional[str] = None,
        required: bool = False,
        default: Any = None,
        type: Optional[Callable[[str], Any]] = None,
        is_flag: bool = False,
    ):
        self.name = name
        self.short = short
        self.required = required
        self.default = default
        self.type = type
        self.is_flag = is_flag

    @property
    def expects_value(self) -> bool:
        """Return True if this flag expects a value when used without '='."""
        return not self.is_flag

    def convert(self, value: str) -> Any:
        """Convert a raw string value to the declared type."""
        if self.type is not None:
            try:
                if self.type is bool:
                    return self._boolify(value)
                return self.type(value)
            except (TypeError, ValueError) as exc:
                raise ParseError(
                    f"ERROR: Value for --{self.name} could not be converted to "
                    f"{self.type.__name__}: {value!r}"
                ) from exc

        # No explicit type: try literal_eval, fall back to string.
        try:
            return literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    @staticmethod
    def _boolify(value: str) -> bool:
        """Convert common string representations to a boolean."""
        if isinstance(value, bool):
            return value
        lowered = str(value).lower()
        if lowered in ("true", "1", "yes", "on"):
            return True
        if lowered in ("false", "0", "no", "off"):
            return False
        raise ValueError(f"Cannot interpret {value!r} as boolean")
