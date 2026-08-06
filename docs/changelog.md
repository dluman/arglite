# Changelog

## 0.30.0

### Added

- Automated PyPI release workflow triggered by version tags.

### Changed

- Bumped version to 0.30.0.

## 0.20.0

### Added

- Explicit flag declaration API: `parser.require()`, `parser.optional()`, `parser.flag()`.
- YAML configuration via `.arglite.yaml` and `parser.load()`.
- Automatic short flags derived from the first letter of each flag name.
- Type conversion for `str`, `int`, `float`, and `bool`.
- `choices` validation.
- Built-in help output with a Rich table.
- JSON Schema validation for YAML configs.
- Full test suite and ReadTheDocs documentation.

### Removed

- Source-code reflection approach for detecting required vs optional flags.
- `vurze` dependency.
