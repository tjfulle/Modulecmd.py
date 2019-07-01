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

    pymod.mc.unuse(tmpdir.strpath)
    alias = pymod.modulepath.get('a-alias')
    assert alias is None

    pymod.alias.remove('a-alias')
