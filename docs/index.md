# arglite

A lightweight, explicit argument parsing library for Python programs.

arglite is for when you want a simple CLI parser without the boilerplate of `argparse`. Declare your flags, access them as attributes, and get on with your program.

## Quick example

```python title="demo.py"
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
python demo.py --name Yo --count 5 --verbose
```

Output:

```text
Yo
5
True
```

## Why arglite?

- **Explicit declarations** — no reflection, no source-code scanning, no magic.
- **Short syntax** — `-n` is automatically derived from `--name`.
- **Type conversion** — get `int`, `float`, `bool`, or raw strings.
- **YAML config** — move flag metadata into `.arglite.yaml`.
- **Help built-in** — `-h` / `--help` prints a Rich table of all flags.

## Where to go next

- [Installation](installation.md)
- [Usage](usage.md)
- [YAML configuration](yaml-config.md)
- [API reference](api.md)
- [Changelog](changelog.md)
