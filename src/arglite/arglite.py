import re
import sys
from ast import literal_eval
from typing import Any, Callable, Optional

from rich.console import Console
from rich.table import Table


class ParseError(Exception):
    """Raised when CLI arguments cannot be parsed correctly."""


class RequirementError(Exception):
    """Raised when a required argument is missing."""


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


class Parser:
    """A lightweight, explicit CLI argument parser."""

    _VALID_FLAG_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")

    def __init__(self):
        self._flags: dict[str, Flag] = {}
        self._short_map: dict[str, str] = {}
        self._values: dict[str, Any] = {}
        self._parsed = False

    def require(
        self,
        name: str,
        short: Optional[str] = None,
        type: Optional[Callable[[str], Any]] = None,
    ) -> "Parser":
        """Declare a required flag."""
        self._declare(name, short=short, required=True, default=None, type=type)
        return self

    def optional(
        self,
        name: str,
        short: Optional[str] = None,
        default: Any = None,
        type: Optional[Callable[[str], Any]] = None,
    ) -> "Parser":
        """Declare an optional flag with an optional default value."""
        self._declare(name, short=short, required=False, default=default, type=type)
        return self

    def flag(self, name: str, short: Optional[str] = None) -> "Parser":
        """Declare a boolean flag (True if present, False otherwise)."""
        self._declare(
            name, short=short, required=False, default=False, type=bool, is_flag=True
        )
        return self

    def _declare(
        self,
        name: str,
        short: Optional[str],
        required: bool,
        default: Any,
        type: Optional[Callable[[str], Any]],
        is_flag: bool = False,
    ) -> None:
        if not isinstance(name, str) or not self._VALID_FLAG_NAME.match(name):
            raise ValueError(f"Invalid flag name: {name!r}")
        if name in self._flags:
            raise ValueError(f"Flag already declared: {name!r}")

        auto_short = self._auto_short(name, short)
        if auto_short and auto_short in self._short_map:
            raise ValueError(
                f"Short flag '-{auto_short}' is already used by "
                f"--{self._short_map[auto_short]}"
            )

        self._flags[name] = Flag(
            name,
            short=auto_short,
            required=required,
            default=default,
            type=type,
            is_flag=is_flag,
        )
        if auto_short:
            self._short_map[auto_short] = name

    def _auto_short(self, name: str, short: Optional[str]) -> Optional[str]:
        """Resolve the short alias for a flag."""
        if short is not None:
            if not isinstance(short, str) or len(short) != 1 or not short.isalpha():
                raise ValueError(
                    f"Invalid short flag for --{name}: {short!r} "
                    "(must be a single letter)"
                )
            return short.lower()

        first = name[0].lower()
        if first not in self._short_map:
            return first
        return None

    def _canonical(self, name: str) -> str:
        """Map a parsed flag name to its canonical declared name."""
        if name in self._flags:
            return name
        if name in self._short_map:
            return self._short_map[name]
        return name

    def _parse(self, argv: list[str]) -> None:
        """Parse argv into flag/value pairs."""
        if self._parsed:
            return

        # Help request: show help and exit.
        if any(arg in ("-h", "--help") for arg in argv):
            self._show_help()

        raw = self._tokenize(argv)
        for provided in raw:
            if provided not in self._flags:
                raise ParseError(
                    f"ERROR: Unknown flag --{provided}; the program does not call for it"
                )

        for name, flag in self._flags.items():
            if name in raw:
                values = raw[name]
                if not flag.expects_value:
                    # Boolean flag: presence means True; an explicit value is
                    # parsed as a boolean (e.g. --verbose=false).
                    if values:
                        self._values[name] = flag.convert(values[-1])
                    else:
                        self._values[name] = True
                else:
                    if not values:
                        raise ParseError(
                            f"ERROR: --{name} was provided without a value"
                        )
                    self._values[name] = flag.convert(values[-1])
            else:
                if flag.required:
                    raise RequirementError(
                        f"ERROR: --{name} is required but was not provided"
                    )
                self._values[name] = flag.default

        self._parsed = True

    def _show_help(self) -> None:
        """Print help and exit cleanly."""
        console = Console()
        console.print(str(self))
        self.display()
        sys.exit(0)

    def _tokenize(self, argv: list[str]) -> dict[str, list[str]]:
        """Tokenize argv into a mapping of canonical flag names to raw values."""
        result: dict[str, list[str]] = {}
        i = 0
        while i < len(argv):
            arg = argv[i]
            raw_name, inline_value = self._split_flag(arg)

            if raw_name is None:
                raise ParseError(
                    f"ERROR: Unexpected positional argument: {arg!r}"
                )

            name = self._canonical(raw_name)
            flag = self._flags.get(name)

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

    def _split_flag(self, arg: str) -> tuple[Optional[str], Optional[str]]:
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

    def _ensure_parsed(self) -> None:
        if not self._parsed:
            try:
                self._parse(sys.argv[1:])
            except (ParseError, RequirementError) as exc:
                console = Console(stderr=True)
                console.print(f"✗ {exc}")
                sys.exit(1)
            except Exception as exc:
                raise ParseError(f"ERROR: Unexpected parser failure: {exc}") from exc

    def __getattribute__(self, name: str) -> Any:
        # Always allow access to internal attributes and methods.
        if name.startswith("_") or name in ("require", "optional", "flag"):
            return super().__getattribute__(name)

        # Declared flags are resolved lazily against sys.argv.
        flags = super().__getattribute__("_flags")
        if name in flags:
            super().__getattribute__("_ensure_parsed")()
            return super().__getattribute__("_values")[name]

        return super().__getattribute__(name)

    def __dir__(self):
        base = list(super().__dir__())
        base.extend(self._flags.keys())
        return sorted(set(base))

    def __str__(self) -> str:
        return "arglite\n\nA lightweight, explicit CLI argument parser.\n"

    def display(self) -> None:
        """Display a help table of all declared flags."""
        table = Table(title="CLI flags")
        table.add_column("Variable name")
        table.add_column("Short flag")
        table.add_column("Variable type")
        table.add_column("Default")
        table.add_column("Required")

        for name, flag in self._flags.items():
            short = f"-{flag.short}" if flag.short else ""
            table.add_row(
                f"--{name}",
                short,
                flag.type.__name__ if flag.type else "inferred",
                str(flag.default),
                "yes" if flag.required else "no",
            )

        console = Console()
        console.print(table)


# Global parser instance.
parser = Parser()
