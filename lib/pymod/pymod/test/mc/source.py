import pytest

import pymod.mc
import pymod.modulepath


@pytest.fixture()
def script(tmpdir):
    f = tmpdir.join("script")
    f.write("echo FOO")
    return f.strpath


@pytest.mark.unit
def test_mc_source_command(script):
    pymod.mc.source(script)
    assert len(pymod.environ.environ.files_to_source) == 1
    file_to_source, _ = pymod.environ.environ.files_to_source[0]
    assert file_to_source == script
    pymod.environ.environ.files_to_source = []
