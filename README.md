# arglite

A lightweight, dynamic argument parsing library for Python programs with klugy support for typing variables.

## Usage

Check this out, `main`:

```python
import arglite

def main():
  print(arglite.parser.a)
  print(arglite.parser.b)
  print(arglite.parser.c)

if __name__ == "__main__":
  main()
```

Run using `pyton main.py -a Yo -b that's -c`.

## Notes

* No automatic `-h` flag yet; soon?
* Flags with no value are automatically converted to `True` boolean
* The module uses `ast.literal_eval`, so `"{'a':'b'}"` will convert to a `dict` (all quotes required)
