import pytest

import pymod.mc
import pymod.modulepath


@pytest.fixture()
def script(tmpdir):
    f = tmpdir.join('script')
    f.write('echo FOO')
    return f.strpath


@pytest.mark.unit
def test_mc_source_command(script, capsys):
    pymod.mc.source(script)
    captured = capsys.readouterr()
    command = r'source {0};'.format(script)
    assert captured[0].strip() == command.strip()
