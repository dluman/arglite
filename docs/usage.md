# Usage

## Declaring flags

Declare flags with the global `parser` instance:

```python
import arglite

arglite.parser.require("name", type=str)
arglite.parser.optional("count", default=1, type=int)
arglite.parser.flag("verbose")
```

| Method | Purpose |
|--------|---------|
| `parser.require(name, type=None)` | Required flag. Exits with an error if missing. |
| `parser.optional(name, default=None, type=None)` | Optional flag with a default value. |
| `parser.flag(name)` | Boolean flag. `True` if present, otherwise `False`. |

## Accessing values

Access declared flags as attributes on the parser. The first time you access a flag, arglite parses `sys.argv`.

```python
print(arglite.parser.name)
print(arglite.parser.count)
print(arglite.parser.verbose)
```

## Short flags

If you do not provide a `short` alias, the first letter of the flag name is used automatically.

```python
arglite.parser.require("name")
```

All of these work:

```bash
python demo.py --name Yo
python demo.py -n Yo
python demo.py --name=Yo
python demo.py -n=Yo
```

You can also set an explicit short alias:

```python
arglite.parser.require("name", short="x")
```

## Types

arglite converts values automatically.

```python
arglite.parser.require("count", type=int)
arglite.parser.require("ratio", type=float)
arglite.parser.optional("debug", default=False, type=bool)
```

Boolean flags are the easiest way to get a simple on/off switch:

```python
arglite.parser.flag("verbose")
```

- `--verbose` → `True`
- absent → `False`
- `--verbose=false` → `False`

## Edge cases

### Values with spaces

Use normal shell quoting:

```bash
python demo.py --message "hello world"
```

### Empty strings

Empty strings are preserved:

```bash
python demo.py --name ""
```

### Negative numbers

Values that start with `-` are handled correctly when they follow a value-expecting flag:

```bash
python demo.py --offset -5
```

## Errors

arglite exits with code 1 and a clear message when something is wrong:

```text
✗ ERROR: --name is required but was not provided
✗ ERROR: Unknown flag --foo; the program does not call for it
✗ ERROR: Value for --count could not be converted to int: 'abc'
```
