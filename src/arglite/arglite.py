import re
import sys
from typing import Any, Callable, Optional

from rich.console import Console

from .config import load_yaml
from .exceptions import ParseError, RequirementError
from .flag import Flag
from . import help as help_module
from . import parse


class Parser:
    """A lightweight, explicit CLI argument parser.

    Flags are declared with `require()`, `optional()`, or `flag()`. Values are
    accessed as attributes on the parser instance. Parsing happens lazily the
    first time a declared flag is accessed.

    If a `.arglite.yaml` file exists in the current working directory, it is
    loaded automatically. Use `load()` to load a different YAML file explicitly.
    """

    _VALID_FLAG_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")
    _DEFAULT_CONFIG = ".arglite.yaml"

    def __init__(self):
        self._flags: dict[str, Flag] = {}
        self._python_flags: set[str] = set()
        self._yaml_flags: set[str] = set()
        self._values: dict[str, Any] = {}
        self._parsed = False
        self._load_yaml(self._DEFAULT_CONFIG, optional=True)

    def load(self, path: str = _DEFAULT_CONFIG) -> "Parser":
        """Load flag declarations from a YAML file.

        This replaces any previously loaded YAML-backed declarations while
        preserving flags declared in Python code.

        Args:
            path: Path to the YAML config file. Defaults to `.arglite.yaml`.

        Returns:
            The parser instance, for chaining.
        """
        self._load_yaml(path, optional=False)
        return self

    def _load_yaml(self, path: str, optional: bool) -> None:
        """Load declarations from a YAML file and merge them."""
        # Remove flags from the previous YAML load that are not also declared
        # in Python. This makes explicit load() calls replace earlier config.
        for name in self._yaml_flags:
            if name not in self._python_flags:
                del self._flags[name]
        self._yaml_flags.clear()

        yaml_flags = load_yaml(path, optional=optional)
        for name, flag in yaml_flags.items():
            self._yaml_flags.add(name)
            if name in self._flags:
                # Python declarations already exist; merge YAML metadata only.
                existing = self._flags[name]
                existing.help = flag.help if flag.help is not None else existing.help
                existing.choices = (
                    flag.choices if flag.choices is not None else existing.choices
                )
                # Only set short alias from YAML if Python did not specify one
                # and the candidate short alias is not already in use.
                if existing.short is None and flag.short is not None:
                    if not any(
                        f.short == flag.short
                        for f in self._flags.values()
                        if f.name != name
                    ):
                        existing.short = flag.short
                continue

            # No Python declaration exists; adopt the YAML declaration directly.
            resolved_short = self._resolve_short(name, flag.short)
            flag.short = resolved_short
            self._flags[name] = flag

    def require(
        self,
        name: str,
        short: Optional[str] = None,
        type: Optional[Callable[[str], Any]] = None,
    ) -> "Parser":
        """Declare a required flag.

        Args:
            name: The flag name. Will be accessed as `parser.name`.
            short: Optional single-letter short alias.
            type: Callable to convert the raw string value.

        Returns:
            The parser instance, for chaining.
        """
        self._declare(name, short=short, required=True, default=None, type=type)
        return self

    def optional(
        self,
        name: str,
        short: Optional[str] = None,
        default: Any = None,
        type: Optional[Callable[[str], Any]] = None,
    ) -> "Parser":
        """Declare an optional flag with an optional default value.

        Args:
            name: The flag name. Will be accessed as `parser.name`.
            short: Optional single-letter short alias.
            default: Value returned when the flag is not provided.
            type: Callable to convert the raw string value.

        Returns:
            The parser instance, for chaining.
        """
        self._declare(name, short=short, required=False, default=default, type=type)
        return self

    def flag(self, name: str, short: Optional[str] = None) -> "Parser":
        """Declare a boolean flag (True if present, False otherwise).

        Args:
            name: The flag name. Will be accessed as `parser.name`.
            short: Optional single-letter short alias.

        Returns:
            The parser instance, for chaining.
        """
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
        if name in self._python_flags:
            raise ValueError(f"Flag already declared: {name!r}")

        resolved_short = self._resolve_short(name, short)
        self._python_flags.add(name)

        if name in self._flags:
            # A YAML declaration already exists; Python wins for behavior, but
            # keep YAML metadata like help and choices.
            existing = self._flags[name]
            existing.required = required
            existing.default = default
            existing.type = type
            existing.is_flag = is_flag
            existing.short = resolved_short
            return

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
                    converted = flag.convert(values[-1])
                    self._validate_choice(flag, converted)
                    self._values[name] = converted
            else:
                if flag.required:
                    raise RequirementError(
                        f"ERROR: --{name} is required but was not provided"
                    )
                self._values[name] = flag.default

        self._parsed = True

    def _validate_choice(self, flag: Flag, value: Any) -> None:
        """Validate a converted value against declared choices."""
        if flag.choices is not None and value not in flag.choices:
            choices = ", ".join(str(c) for c in flag.choices)
            raise ParseError(
                f"ERROR: Value for --{flag.name} must be one of: {choices}; "
                f"got {value!r}"
            )

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
