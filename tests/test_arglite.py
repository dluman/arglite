import pytest
import sys

from arglite import Parser, ParseError, RequirementError


@pytest.fixture
def parser():
    """Return a fresh Parser instance for each test."""
    return Parser()


class TestDeclarations:
    def test_require_flag(self, parser):
        parser.require("name")
        assert parser._flags["name"].required is True
        assert parser._flags["name"].default is None
        assert parser._flags["name"].type is None

    def test_optional_flag_with_default(self, parser):
        parser.optional("count", default=1, type=int)
        assert parser._flags["count"].required is False
        assert parser._flags["count"].default == 1
        assert parser._flags["count"].type is int

    def test_flag_is_bool(self, parser):
        parser.flag("verbose")
        assert parser._flags["verbose"].type is bool
        assert parser._flags["verbose"].default is False

    def test_invalid_flag_name(self, parser):
        with pytest.raises(ValueError):
            parser.require("123")
        with pytest.raises(ValueError):
            parser.require("")

    def test_duplicate_flag_name(self, parser):
        parser.require("name")
        with pytest.raises(ValueError):
            parser.require("name")

    def test_explicit_short_flag(self, parser):
        parser.require("name", short="x")
        assert parser._flags["name"].short == "x"
        assert parser._short_map["x"] == "name"

    def test_auto_short_conflict_is_silent(self, parser):
        parser.require("name")
        # Auto-assigned short 'n' is already taken by --name.
        parser.flag("nested")
        # --nested gets no short alias; --name keeps '-n'.
        assert parser._flags["nested"].short is None

    def test_explicit_short_flag_conflict(self, parser):
        parser.require("name")
        with pytest.raises(ValueError):
            parser.flag("verbose", short="n")


class TestParsing:
    def test_required_flag_value(self, parser):
        parser.require("name")
        parser._parse(["--name", "Yo"])
        assert parser._values["name"] == "Yo"

    def test_short_flag(self, parser):
        parser.require("name")
        parser._parse(["-n", "Yo"])
        assert parser._values["name"] == "Yo"

    def test_equals_syntax(self, parser):
        parser.require("name")
        parser._parse(["--name=Yo"])
        assert parser._values["name"] == "Yo"

        parser2 = Parser()
        parser2.require("name")
        parser2._parse(["-n=Yo"])
        assert parser2._values["name"] == "Yo"

    def test_optional_default(self, parser):
        parser.optional("count", default=1, type=int)
        parser._parse([])
        assert parser._values["count"] == 1

    def test_optional_override(self, parser):
        parser.optional("count", default=1, type=int)
        parser._parse(["--count", "42"])
        assert parser._values["count"] == 42

    def test_flag_present(self, parser):
        parser.flag("verbose")
        parser._parse(["--verbose"])
        assert parser._values["verbose"] is True

    def test_flag_absent(self, parser):
        parser.flag("verbose")
        parser._parse([])
        assert parser._values["verbose"] is False

    def test_flag_with_value_still_true(self, parser):
        parser.flag("verbose")
        parser._parse(["--verbose=true"])
        assert parser._values["verbose"] is True

    def test_flag_with_value_false(self, parser):
        parser.flag("verbose")
        parser._parse(["--verbose=false"])
        assert parser._values["verbose"] is False

    def test_type_conversion_int(self, parser):
        parser.require("count", type=int)
        parser._parse(["--count", "42"])
        assert parser._values["count"] == 42
        assert isinstance(parser._values["count"], int)

    def test_type_conversion_float(self, parser):
        parser.require("ratio", type=float)
        parser._parse(["--ratio", "3.14"])
        assert parser._values["ratio"] == 3.14

    def test_type_conversion_bool(self, parser):
        parser.optional("debug", default=False, type=bool)
        parser._parse(["--debug", "true"])
        assert parser._values["debug"] is True

        parser2 = Parser()
        parser2.optional("debug", default=True, type=bool)
        parser2._parse(["--debug", "false"])
        assert parser2._values["debug"] is False

    def test_value_with_spaces(self, parser):
        # A single shell-quoted value containing spaces is preserved as one token.
        parser.require("message")
        parser._parse(["--message", "hello world"])
        assert parser._values["message"] == "hello world"

    def test_multiple_values_after_flag_rejected(self, parser):
        # Without quoting, each token is separate; the second token is positional.
        parser.require("message")
        with pytest.raises(ParseError):
            parser._parse(["--message", "hello", "world"])

    def test_empty_string_value(self, parser):
        parser.require("message")
        parser._parse(["--message", ""])
        assert parser._values["message"] == ""

    def test_negative_number_value(self, parser):
        parser.require("offset", type=int)
        parser._parse(["--offset", "-5"])
        assert parser._values["offset"] == -5

    def test_literal_eval_list(self, parser):
        parser.require("items")
        parser._parse(["--items", "[1, 2, 3]"])
        assert parser._values["items"] == [1, 2, 3]

    def test_literal_eval_dict(self, parser):
        parser.require("config")
        parser._parse(["--config", "{'a': 'b'}"])
        assert parser._values["config"] == {"a": "b"}

    def test_underscore_and_hyphen_flag_names(self, parser):
        parser.require("file_name")
        parser._parse(["--file_name", "x"])
        assert parser._values["file_name"] == "x"

        parser2 = Parser()
        parser2.require("file-name")
        parser2._parse(["--file-name", "x"])
        assert parser2._values["file-name"] == "x"


class TestErrors:
    def test_missing_required_flag(self, parser):
        parser.require("name")
        with pytest.raises(RequirementError):
            parser._parse([])

    def test_flag_without_value(self, parser):
        parser.require("name")
        with pytest.raises(ParseError):
            parser._parse(["--name"])

    def test_unknown_flag(self, parser):
        parser.require("name")
        with pytest.raises(ParseError):
            parser._parse(["--name", "Yo", "--extra", "oops"])

    def test_invalid_type_conversion(self, parser):
        parser.require("count", type=int)
        with pytest.raises(ParseError):
            parser._parse(["--count", "abc"])

    def test_positional_argument_rejected(self, parser):
        parser.require("name")
        with pytest.raises(ParseError):
            parser._parse(["positional", "--name", "Yo"])


class TestAccess:
    def test_attribute_access(self, parser, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["script", "--name", "Yo"])
        parser.require("name")
        assert parser.name == "Yo"

    def test_attribute_access_unparsed(self, parser, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["script", "--name", "Yo"])
        parser.require("name")
        # Accessing the attribute triggers parsing.
        assert parser._parsed is False
        _ = parser.name
        assert parser._parsed is True


class TestHelp:
    def test_help_flag_exits(self, parser):
        parser.require("name")
        with pytest.raises(SystemExit) as exc_info:
            parser._parse(["-h"])
        assert exc_info.value.code == 0

    def test_help_long_flag_exits(self, parser):
        parser.require("name")
        with pytest.raises(SystemExit) as exc_info:
            parser._parse(["--help"])
        assert exc_info.value.code == 0
