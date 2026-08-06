# Installation

## From PyPI

```bash
pip install arglite
```

## With uv

```bash
uv add arglite
```

## Development setup

```bash
git clone https://github.com/dougluman/arglite.git
cd arglite
uv sync --extra dev
```

Run the tests:

```bash
uv run --with pytest pytest tests/
```

## Documentation dependencies

To build the docs locally:

```bash
uv sync --extra docs
uv run --extra docs mkdocs serve
```
