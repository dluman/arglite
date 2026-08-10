# arglite

[![PyPI version](https://img.shields.io/pypi/v/arglite)](https://pypi.org/project/arglite/)
[![Documentation Status](https://readthedocs.org/projects/arglite/badge/?version=latest)](https://arglite.readthedocs.io/en/latest/?badge=latest)

A lightweight, explicit argument parsing library for Python programs.

I made this for a teaching machine project I'm working on (I needed a custom argument parser for _reasons_), and I'm always too impatient to use `argparse`.

## Quick start

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

```bash
python main.py --name Yo --count 5 --verbose
```

## YAML configuration

You can also declare flags in a `.arglite.yaml` file in the working directory. arglite loads it automatically, or you can point to a different file with `parser.load()`.

```yaml
flags:
  name:
    help: "The user name"
    type: str
    required: true

  count:
    help: "Number of items"
    type: int
    default: 1

  verbose:
    help: "Enable verbose output"
    action: store_true
```

```python
import arglite

print(arglite.parser.name)
print(arglite.parser.count)
print(arglite.parser.verbose)
```

Python declarations override YAML for runtime behavior (`type`, `required`, `default`, `action`), while YAML metadata like `help` and `choices` is merged in.

## Documentation

Full documentation is available at [arglite.readthedocs.io](https://arglite.readthedocs.io/).

## Installation

```bash
pip install arglite
```

## Notes

- Flags are case-sensitive.
- Both `-f` / `--flag` and `--flag=value` / `-f=value` syntaxes are supported.
- Values containing spaces work when passed via the shell's normal quoting rules.
- Empty string values (`--name ""`) are preserved.
- `ast.literal_eval` is used for type inference when no explicit `type` is given.
