# arglite

[![PyPI version](https://img.shields.io/pypi/v/arglite)](https://pypi.org/project/arglite/)

A lightweight, dynamic argument parsing library for Python programs with klugy support for typing variables.

I made this for a teaching machine project I'm working on (I needed a custom argument parser for _reasons_),
and I'm always too impatient to use `argparse`.

## Installation

Find this tool on `PyPI`: `pip install arglite`

## Usage

Check this out:

```python
import arglite

def main():
  # Can include explicit requirement
  print(arglite.parser.required.a)
  # Can be an implicit requirement
  print(arglite.parser.b)
  # Can also be purely optional
  print(arglite.parser.optional.c)
  print(arglite.parser.optional.d)

if __name__ == "__main__":
  main()
```

Run using `python main.py -a Yo --b that is -c`.

For the more intrepid among us, this also works:

```python
from arglite import parser as cliarg

def main():
  # Can include explicit requirement
  print(cliarg.required.a)
  # Can be an implicit requirement
  print(cliarg.b)
  # Can also be purely optional
  print(cliarg.optional.c)
  print(cliarg.optional.d)

if __name__ == "__main__":
  main()
```

### HELP!

Help now appears when no variables are provided or when requested by use of `-h` (`--h`) or `-help` (`--help`).

### Errors

When errors are present (i.e. flags are provided which aren't used in the code _or_ flags used aren't provided),
you'll see errors:

```
✗ ERROR: A value was provided for A, but the program doesn't call for it
✗ ERROR: A value was expected for a, but not was provided as a flag
✗ ERROR: A value was expected for b, but not was provided as a flag
```


## Notes

* Flags with no value are automatically converted to `True` boolean
* The module uses `ast.literal_eval`, so `"{'a':'b'}"` will convert to a `dict` (all quotes required)
