import os
import pytest

import modulecmd.system
import modulecmd.paths
import modulecmd.environ
import modulecmd.alias


def test_alias_save(tmpdir, mock_modulepath):

    tmpdir.join("a.py").write("")
    mock_modulepath(tmpdir.strpath)

    target = modulecmd.modulepath.get("a")
    modulecmd.alias.save(target, "a-alias")

    x = modulecmd.alias.get("a-alias")
    assert x is not None
    assert os.path.isfile(x["filename"])
    alias = modulecmd.modulepath.get("a-alias")
    assert alias is not None
    assert alias.file == target.file

    s = modulecmd.alias.avail()
    assert "a-alias" in s

    s = modulecmd.alias.avail(terse=True)
    assert "a-alias" in s

    aliases = modulecmd.alias.get(tmpdir.strpath)
    assert len(aliases) == 1
    the_alias = aliases[0]
    assert the_alias[0] == "a-alias"
    assert the_alias[1] == "a"

    # If an alias is loaded, and its modulepath is not being used, its
    # modulepath will be appended to modulecmd.modulepath
    modulecmd.system.unuse(tmpdir.strpath)
    assert tmpdir.strpath not in modulecmd.modulepath._path
    alias = modulecmd.modulepath.get("a-alias")
    assert alias is not None
    assert tmpdir.strpath in modulecmd.modulepath._path

    modulecmd.alias.remove("a-alias")
