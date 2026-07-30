import pytest

from arglite import Parser


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

    def test_help_table_includes_declarations(self, parser, capsys):
        parser.require("name", type=str)
        parser.optional("count", default=1, type=int)
        parser.flag("verbose")
        with pytest.raises(SystemExit):
            parser._parse(["--help"])
        captured = capsys.readouterr()
        assert "--name" in captured.out
        assert "--count" in captured.out
        assert "--verbose" in captured.out
        assert "-n" in captured.out
        assert "-c" in captured.out
        assert "-v" in captured.out
