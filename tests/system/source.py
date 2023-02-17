import pytest

import modulecmd.system
import modulecmd.modulepath


@pytest.fixture()
def script(tmpdir):
    f = tmpdir.join("script")
    f.write("echo FOO")
    return f.strpath


@pytest.mark.unit
def test_mc_source_command(script):
    modulecmd.system.source(script)
    assert len(modulecmd.environ.environ.files_to_source) == 1
    file_to_source, _ = modulecmd.environ.environ.files_to_source[0]
    assert file_to_source == script
    modulecmd.environ.environ.files_to_source = []
