import os
import tempfile

import pytest

from arglite import Parser, ParseError


@pytest.fixture
def parser():
    return Parser()


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


def write_yaml(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


class TestExplicitLoad:
    def test_load_yaml_declarations(self, parser, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  name:
    type: str
    required: true
    help: "The user name"
  count:
    type: int
    default: 1
    help: "Number of items"
  verbose:
    action: store_true
    help: "Enable verbose output"
""",
        )
        parser.load(path)
        parser._parse(["--name", "Yo", "--count", "5", "--verbose"])
        assert parser._values["name"] == "Yo"
        assert parser._values["count"] == 5
        assert parser._values["verbose"] is True
        assert parser._flags["name"].help == "The user name"

    def test_load_missing_file_raises(self, parser, temp_dir):
        path = os.path.join(temp_dir, "missing.yaml")
        with pytest.raises(ParseError):
            parser.load(path)

    def test_load_replaces_yaml_flags(self, parser, temp_dir):
        path1 = os.path.join(temp_dir, "a.yaml")
        path2 = os.path.join(temp_dir, "b.yaml")
        write_yaml(
            path1,
            """
flags:
  alpha:
    type: str
""",
        )
        write_yaml(
            path2,
            """
flags:
  beta:
    type: int
    default: 10
""",
        )
        parser.load(path1)
        parser.load(path2)
        parser._parse([])
        assert "alpha" not in parser._flags
        assert parser._values["beta"] == 10

    def test_load_preserves_python_flags(self, parser, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  name:
    type: str
    help: "from yaml"
""",
        )
        parser.require("name", type=str)
        parser.load(path)
        assert parser._flags["name"].help == "from yaml"
        parser._parse(["--name", "Yo"])
        assert parser._values["name"] == "Yo"


class TestAutoLoad:
    def test_autoload_arglite_yaml(self, temp_dir):
        path = os.path.join(temp_dir, ".arglite.yaml")
        write_yaml(
            path,
            """
flags:
  name:
    type: str
    required: true
    help: "The user name"
""",
        )
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            p = Parser()
            p._parse(["--name", "Yo"])
            assert p._values["name"] == "Yo"
            assert p._flags["name"].help == "The user name"
        finally:
            os.chdir(old_cwd)

    def test_autoload_missing_is_silent(self, temp_dir):
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            p = Parser()
            p.flag("verbose")
            p._parse(["--verbose"])
            assert p._values["verbose"] is True
        finally:
            os.chdir(old_cwd)


class TestMergeSemantics:
    def test_python_overrides_yaml_type(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  count:
    type: str
    help: "from yaml"
""",
        )
        parser = Parser()
        parser.load(path)
        parser.optional("count", default=1, type=int)
        assert parser._flags["count"].type is int
        assert parser._flags["count"].help == "from yaml"
        parser._parse(["--count", "42"])
        assert parser._values["count"] == 42

    def test_python_overrides_yaml_required(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  name:
    type: str
    required: true
    help: "from yaml"
""",
        )
        parser = Parser()
        parser.load(path)
        parser.optional("name")
        assert parser._flags["name"].required is False
        parser._parse([])
        assert parser._values["name"] is None

    def test_yaml_metadata_kept_when_python_declares(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  mode:
    type: str
    choices: ["fast", "slow"]
    help: "Processing mode"
""",
        )
        parser = Parser()
        parser.load(path)
        parser.optional("mode", default="fast")
        assert parser._flags["mode"].choices == ["fast", "slow"]
        assert parser._flags["mode"].help == "Processing mode"


class TestChoices:
    def test_choices_valid(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  mode:
    type: str
    choices: ["fast", "slow", "balanced"]
    default: "fast"
""",
        )
        parser = Parser()
        parser.load(path)
        parser._parse(["--mode", "slow"])
        assert parser._values["mode"] == "slow"

    def test_choices_invalid(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  mode:
    type: str
    choices: ["fast", "slow", "balanced"]
    default: "fast"
""",
        )
        parser = Parser()
        parser.load(path)
        with pytest.raises(ParseError):
            parser._parse(["--mode", "turbo"])


class TestYamlErrors:
    def test_unknown_type(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  count:
    type: decimal
""",
        )
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)

    def test_invalid_action(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  verbose:
    action: toggle
""",
        )
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)

    def test_invalid_required(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  name:
    required: "yes"
""",
        )
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)

    def test_flags_not_mapping(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags: ["a", "b"]
""",
        )
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)

    def test_flag_spec_not_mapping(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(
            path,
            """
flags:
  name: "just a string"
""",
        )
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)

    def test_invalid_yaml(self, temp_dir):
        path = os.path.join(temp_dir, "flags.yaml")
        write_yaml(path, "flags: [unclosed")
        parser = Parser()
        with pytest.raises(ParseError):
            parser.load(path)
