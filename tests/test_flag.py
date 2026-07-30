import pytest

from arglite import Flag, ParseError


@pytest.fixture
def flag():
    return Flag("demo")


class TestFlagProperties:
    def test_required_flag_expects_value(self):
        flag = Flag("name", required=True, type=str)
        assert flag.expects_value is True

    def test_optional_flag_expects_value(self):
        flag = Flag("count", default=1, type=int)
        assert flag.expects_value is True

    def test_bool_flag_does_not_expect_value(self):
        flag = Flag("verbose", type=bool, default=False, is_flag=True)
        assert flag.expects_value is False


class TestFlagConversion:
    def test_string_default(self, flag):
        assert flag.convert("hello") == "hello"

    def test_int_conversion(self):
        flag = Flag("count", type=int)
        assert flag.convert("42") == 42
        assert isinstance(flag.convert("42"), int)

    def test_float_conversion(self):
        flag = Flag("ratio", type=float)
        assert flag.convert("3.14") == 3.14

    def test_bool_true_values(self):
        flag = Flag("verbose", type=bool)
        for value in ("true", "True", "1", "yes", "on"):
            assert flag.convert(value) is True

    def test_bool_false_values(self):
        flag = Flag("verbose", type=bool)
        for value in ("false", "False", "0", "no", "off"):
            assert flag.convert(value) is False

    def test_bool_invalid_raises(self):
        flag = Flag("verbose", type=bool)
        with pytest.raises(ParseError):
            flag.convert("maybe")

    def test_invalid_int_conversion(self):
        flag = Flag("count", type=int)
        with pytest.raises(ParseError):
            flag.convert("abc")

    def test_empty_string_preserved(self, flag):
        assert flag.convert("") == ""

    def test_literal_eval_list(self, flag):
        assert flag.convert("[1, 2, 3]") == [1, 2, 3]

    def test_literal_eval_dict(self, flag):
        assert flag.convert("{'a': 'b'}") == {"a": "b"}

    def test_literal_eval_tuple(self, flag):
        assert flag.convert("(1, 2)") == (1, 2)

    def test_literal_eval_set(self, flag):
        assert flag.convert("{1, 2, 3}") == {1, 2, 3}

    def test_unquoted_string_falls_back(self, flag):
        assert flag.convert("hello world") == "hello world"

    def test_bool_input_passthrough(self):
        flag = Flag("verbose", type=bool)
        assert flag.convert(True) is True
        assert flag.convert(False) is False
