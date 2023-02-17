import subprocess
from modulecmd.util import *
from llnl.util.filesystem import working_dir, touch


def test_util_lang_split():
    assert split(None) == []
    assert split("a,b,c,,d", sep=",") == ["a", "b", "c", "d"]
    assert split(" a  , b,c,,d", sep=",", maxsplit=1) == ["a", "b,c,,d"]


def test_util_lang_join():
    assert join(("a  ", "b  ", "c  "), sep=",", string=lambda x: str(x).strip()) == "a,b,c"


def test_util_lang_boolean():
    assert boolean("off") is False
    assert boolean("on") is True


def test_util_lang_which(tmpdir):
    with working_dir(tmpdir.strpath):
        touch("spam")
        out = subprocess.check_output("chmod +x spam".split())
        assert which("spam") == "spam"
    ls = which("ls")
    assert ls in ("/bin/ls", "/usr/bin/ls")


def test_util_lang_textfill():
    s = "a super long string"
    assert textfill(s) == s
    assert textfill(s, width=8, indent=2) == "  a\n  super\n  long\n  string"


def test_util_lang_get_system_manpath():
    p = get_system_manpath()


def test_util_lang_pop():
    a = [1, 2, 3, 4, 3, 2, 1]
    pop(a, 3)
    assert a == [1, 2, 4, 3, 2, 1]
    a = [1, 2, 3, 4, 3, 2, 1]
    pop(a, 3, from_back=True)
    assert a == [1, 2, 3, 4, 2, 1]
