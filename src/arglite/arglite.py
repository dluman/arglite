import re
import sys
from typing import Any, Callable, Optional

from rich.console import Console

from .exceptions import ParseError, RequirementError
from .flag import Flag
from . import help as help_module
from . import parse


class Parser:
    """A lightweight, explicit CLI argument parser."""

    _VALID_FLAG_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")

    def __init__(self):
        self._flags: dict[str, Flag] = {}
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

        resolved_short = self._resolve_short(name, short)
        self._flags[name] = Flag(
            name,
            short=resolved_short,
            required=required,
            default=default,
            type=type,
            is_flag=is_flag,
        )

    def _resolve_short(
        self, name: str, short: Optional[str]
    ) -> Optional[str]:
        """Resolve the short alias for a flag."""
        if short is not None:
            if not isinstance(short, str) or len(short) != 1 or not short.isalpha():
                raise ValueError(
                    f"Invalid short flag for --{name}: {short!r} "
                    "(must be a single letter)"
                )
            short = short.lower()
            for flag in self._flags.values():
                if flag.short == short:
                    raise ValueError(
                        f"Short flag '-{short}' is already used by --{flag.name}"
                    )
            return short

        first = name[0].lower()
        for flag in self._flags.values():
            if flag.short == first:
                return None
        return first

    def _parse(self, argv: list[str]) -> None:
        """Parse argv into flag/value pairs."""
        if self._parsed:
            return

        # Help request: show help and exit.
        if any(arg in ("-h", "--help") for arg in argv):
            self._show_help()

        raw = parse.tokenize(argv, self._flags)
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
        help_module.show_summary()
        help_module.render(self._flags)
        sys.exit(0)

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


# Global parser instance.
parser = Parser()
