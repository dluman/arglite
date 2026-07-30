import pytest

from arglite import Flag, ParseError
from arglite.parse import tokenize


def make_flags(**kwargs):
    """Helper to build a flag dict for tokenization tests."""
    return {
        name: Flag(name, **spec)
        for name, spec in kwargs.items()
    }


class TestLongFlags:
    def test_long_flag_value(self):
        flags = make_flags(name={"type": str})
        assert tokenize(["--name", "Yo"], flags) == {"name": ["Yo"]}

    def test_long_equals_syntax(self):
        flags = make_flags(name={"type": str})
        assert tokenize(["--name=Yo"], flags) == {"name": ["Yo"]}

    def test_long_flag_missing_value(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["--name"], flags)

    def test_long_empty_name(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["--"], flags)


class TestShortFlags:
    def test_short_flag_value(self):
        flags = make_flags(name={"type": str, "short": "n"})
        assert tokenize(["-n", "Yo"], flags) == {"name": ["Yo"]}

    def test_short_equals_syntax(self):
        flags = make_flags(name={"type": str, "short": "n"})
        assert tokenize(["-n=Yo"], flags) == {"name": ["Yo"]}

    def test_short_flag_without_declaration(self):
        # Without a declared short alias, '-n' is parsed as a flag named 'n'.
        flags = make_flags(n={"type": str})
        assert tokenize(["-n", "Yo"], flags) == {"n": ["Yo"]}


class TestBooleanFlags:
    def test_boolean_flag_present(self):
        flags = make_flags(verbose={"type": bool, "default": False, "is_flag": True})
        assert tokenize(["--verbose"], flags) == {"verbose": []}

    def test_boolean_flag_with_value(self):
        flags = make_flags(verbose={"type": bool, "default": False, "is_flag": True})
        assert tokenize(["--verbose=false"], flags) == {"verbose": ["false"]}

    def test_boolean_flag_does_not_consume_next(self):
        flags = make_flags(
            verbose={"type": bool, "default": False, "is_flag": True},
            name={"type": str},
        )
        assert tokenize(["--verbose", "--name", "Yo"], flags) == {
            "verbose": [],
            "name": ["Yo"],
        }


class TestValues:
    def test_value_with_spaces(self):
        flags = make_flags(message={"type": str})
        assert tokenize(["--message", "hello world"], flags) == {
            "message": ["hello world"]
        }

    def test_empty_string_value(self):
        flags = make_flags(message={"type": str})
        assert tokenize(["--message", ""], flags) == {"message": [""]}

    def test_negative_number_value(self):
        flags = make_flags(offset={"type": int})
        assert tokenize(["--offset", "-5"], flags) == {"offset": ["-5"]}

    def test_multiple_flags(self):
        flags = make_flags(name={"type": str}, count={"type": int})
        assert tokenize(["--name", "Yo", "--count", "5"], flags) == {
            "name": ["Yo"],
            "count": ["5"],
        }

    def test_repeated_flag_last_value(self):
        flags = make_flags(name={"type": str})
        assert tokenize(["--name", "A", "--name", "B"], flags) == {
            "name": ["A", "B"]
        }


class TestErrors:
    def test_positional_argument(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["positional"], flags)

    def test_positional_after_flag(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["--name", "Yo", "positional"], flags)

    def test_single_dash_is_positional(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["-"], flags)

    def test_value_required_flag_without_value(self):
        flags = make_flags(name={"type": str})
        with pytest.raises(ParseError):
            tokenize(["--name"], flags)

    def test_unknown_flag_not_validated(self):
        # tokenize itself does not reject unknown flags; it just maps names.
        flags = make_flags(name={"type": str})
        assert tokenize(["--extra", "oops"], flags) == {"extra": ["oops"]}
