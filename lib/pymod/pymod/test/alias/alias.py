import os
import pytest

import pymod.mc
import pymod.paths
import pymod.environ
import pymod.alias


def test_alias_save(tmpdir, mock_modulepath):

    tmpdir.join('a.py').write('')
    mock_modulepath(tmpdir.strpath)

    target = pymod.modulepath.get('a')
    pymod.alias.save(target, 'a-alias')

    x = pymod.alias.get('a-alias')
    assert x is not None
    assert os.path.isfile(x['filename'])
    alias = pymod.modulepath.get('a-alias')
    assert alias is not None
    assert alias.filename == target.filename

    s = pymod.alias.avail()
    assert 'a-alias' in s

    s = pymod.alias.avail(terse=True)
    assert 'a-alias' in s

    aliases = pymod.alias.get(tmpdir.strpath)
    assert len(aliases) == 1
    the_alias = aliases[0]
    assert the_alias[0] == 'a-alias'
    assert the_alias[1] == 'a'

    # If an alias is loaded, and its modulepath is not being used, its
    # modulepath will be appended to pymod.modulepath
    pymod.mc.unuse(tmpdir.strpath)
    assert tmpdir.strpath not in pymod.modulepath._path
    alias = pymod.modulepath.get('a-alias')
    assert alias is not None
    assert tmpdir.strpath in pymod.modulepath._path

    pymod.alias.remove('a-alias')
