import pytest

from arglite import ParseError
from arglite.validate import validate_config


class TestSchemaValidation:
    def test_valid_config_passes(self):
        config = {
            "flags": {
                "name": {"type": "str", "required": True, "help": "User name"},
                "count": {"type": "int", "default": 1},
                "verbose": {"action": "store_true", "help": "Verbose"},
            }
        }
        validate_config(config, "test.yaml")  # does not raise

    def test_unknown_top_level_key_allowed(self):
        config = {
            "version": "1.0",
            "flags": {"name": {"type": "str"}},
        }
        validate_config(config, "test.yaml")  # does not raise

    def test_unknown_flag_field_allowed(self):
        config = {
            "flags": {
                "name": {"type": "str", "future_field": [1, 2, 3]},
            }
        }
        validate_config(config, "test.yaml")  # does not raise

    def test_invalid_type_value(self):
        config = {"flags": {"count": {"type": "decimal"}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_invalid_action_value(self):
        config = {"flags": {"verbose": {"action": "toggle"}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_required_not_boolean(self):
        config = {"flags": {"name": {"required": "yes"}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_short_too_long(self):
        config = {"flags": {"name": {"short": "nm"}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_choices_not_array(self):
        config = {"flags": {"mode": {"choices": "fast"}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_help_not_string(self):
        config = {"flags": {"name": {"help": ["not", "a", "string"]}}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_flags_not_object(self):
        config = {"flags": ["name", "count"]}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)

    def test_flag_spec_not_object(self):
        config = {"flags": {"name": "just a string"}}
        with pytest.raises(ParseError) as exc_info:
            validate_config(config, "test.yaml")
        assert "Invalid YAML config" in str(exc_info.value)
