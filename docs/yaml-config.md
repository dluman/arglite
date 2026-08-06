# YAML configuration

You can declare flags in a `.arglite.yaml` file instead of (or alongside) Python declarations.

## Automatic loading

If `.arglite.yaml` exists in the current working directory, arglite loads it automatically when you import the module.

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

## Explicit loading

To load a different file, use `parser.load()`:

```python
arglite.parser.load("custom.yaml")
```

Calling `load()` again replaces the previous YAML-backed declarations while preserving flags declared in Python.

## YAML fields

| Field | Description | Valid values |
|-------|-------------|--------------|
| `type` | Convert the value to this type | `str`, `int`, `float`, `bool` |
| `default` | Default when the flag is absent | any YAML value |
| `required` | Exit if the flag is absent | `true` or `false` |
| `action` | Boolean action | `store_true` or `store_false` |
| `help` | Description shown in help | string |
| `choices` | Allowed values | list |
| `short` | Explicit single-letter short alias | string |

## Merge rules

When a flag is declared in both Python and YAML:

- Python wins for runtime behavior: `type`, `required`, `default`, `action`.
- YAML metadata is merged in: `help`, `choices`.

Example:

```python
arglite.parser.optional("name")  # optional, no type, no default
```

```yaml
flags:
  name:
    type: str
    required: true
    help: "The user name"
```

Result: `name` is optional with a default of `None`, but it has a `help` string and a string type for the help table.

## Choices

Restrict values to a list:

```yaml
flags:
  mode:
    type: str
    choices: ["fast", "slow", "balanced"]
    default: "fast"
```

```bash
python demo.py --mode turbo
# ✗ ERROR: Value for --mode must be one of: fast, slow, balanced; got 'turbo'
```

## Schema validation

`.arglite.yaml` is validated against a JSON Schema at runtime. The schema is lenient: unknown keys are allowed, so you can experiment. Known fields are validated for type and valid values.

The schema is bundled as `arglite/schema.json` in the installed package.
