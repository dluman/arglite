# arglite

[![PyPI version](https://img.shields.io/pypi/v/arglite)](https://pypi.org/project/arglite/)

A lightweight, explicit argument parsing library for Python programs.

I made this for a teaching machine project I'm working on (I needed a custom argument parser for _reasons_), and I'm always too impatient to use `argparse`.

## Installation

Find this tool on `PyPI`: `pip install arglite`

## Usage

Declare the flags your program expects, then access them as attributes on the global `parser`:

```python
import arglite

arglite.parser.require("name", type=str)
arglite.parser.optional("count", default=1, type=int)
arglite.parser.flag("verbose")

def main():
    print(arglite.parser.name)
    print(arglite.parser.count)
    print(arglite.parser.verbose)

if __name__ == "__main__":
    main()
```

Run it with:

```bash
python main.py --name Yo --count 5 --verbose
```

### Declarations

- `parser.require(name, short=None, type=None)` — required flag; exits with an error if missing.
- `parser.optional(name, short=None, default=None, type=None)` — optional flag with an optional default value.
- `parser.flag(name, short=None)` — boolean flag; `True` if present, otherwise `False`.

If `short` is not given, the first letter of the flag name is used automatically (e.g. `--name` can also be `-n`).

### Accessing values

Declared flags are accessed directly on the parser:

```python
arglite.parser.name
arglite.parser.count
arglite.parser.verbose
```

### HELP!

Help appears when `-h` / `--help` is used.

### Errors

When arguments are missing, unknown, or cannot be converted to the declared type, you'll see clear errors:

```
ERROR: --name is required but was not provided
ERROR: Unknown flag --foo; the program does not call for it
ERROR: Value for --count could not be converted to int: 'abc'
```

## Notes

- Flags are case-sensitive.
- Both `-f` / `--flag` and `--flag=value` / `-f=value` syntaxes are supported.
- Values containing spaces work when passed via the shell's normal quoting rules.
- Empty string values (`--name ""`) are preserved.
- `ast.literal_eval` is used for type inference when no explicit `type` is given.
