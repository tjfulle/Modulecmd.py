from pymod.util.lang import *
from llnl.util.filesystem import working_dir, touch


def test_util_lang_listdir(tmpdir):
    with working_dir(tmpdir.strpath):
        touch("foo.txt")
        touch("baz.py")
        touch("spam.py")
        items = listdir(".")
        assert sorted(items) == ["baz.py", "foo.txt", "spam.py"]
        items = listdir(".", key=lambda x: x.endswith(".py"))
        assert sorted(items) == ["baz.py", "spam.py"]


def test_util_lang_split():
    assert split(None) == []
    assert split("a,b,c,,d", sep=",") == ["a", "b", "c", "d"]
    assert split(" a  , b,c,,d", sep=",", num=1) == ["a", "b,c,,d"]


def test_util_lang_join():
    assert join(("a  ", "b  ", "c  "), ",") == "a,b,c"


def test_util_lang_join_args():
    assert join_args("a  ", "b  ", "c  ") == "a   b   c  "


def test_util_lang_boolean():
    assert boolean("off") is False
    assert boolean("on") is True


def test_util_lang_strip_quotes():
    assert strip_quotes('"baz"') == "baz"
    assert strip_quotes("'baz'") == "baz"


def test_util_lang_check_output(tmpdir):
    """Implementation of subprocess's check_output"""
    with working_dir(tmpdir.strpath):
        touch("spam")
        out = check_output(["ls"])
        assert "spam" in out


def test_util_lang_which(tmpdir):
    with working_dir(tmpdir.strpath):
        touch("spam")
        out = check_output(["chmod", "+x", "spam"])
        assert which("spam") == "spam"
    ls = which("ls")
    assert ls in ("/bin/ls", "/usr/bin/ls")


def test_util_lang_textfill():
    s = "a super long string"
    assert textfill(s) == s
    assert textfill(s, width=8, indent=2) == "  a\n  super\n  long\n  string"


def test_util_lang_get_system_manpath():
    p = get_system_manpath()


def test_util_lang_get_processes():
    procs = get_processes()


def test_util_lang_pop():
    a = [1, 2, 3, 4, 3, 2, 1]
    pop(a, 3)
    assert a == [1, 2, 4, 3, 2, 1]
    a = [1, 2, 3, 4, 3, 2, 1]
    pop(a, 3, from_back=True)
    assert a == [1, 2, 3, 4, 2, 1]
