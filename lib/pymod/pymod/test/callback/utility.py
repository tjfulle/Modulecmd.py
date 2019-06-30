import os
import pytest
import pymod.mc
from pymod.callback import get_callback


def test_callback_utility_check_output():
    check_output = get_callback('check_output')
    check_output(None, None, 'ls -l')


def test_callback_utility_colorize():
    colorize = get_callback('colorize')
    s = '@r{RED}'
    red_s = colorize(None, None, s)


def test_callback_utility_listdir(tmpdir):
    listdir = get_callback('listdir')
    check_output = get_callback('check_output')
    tmpdir.join('foo').write('')
    tmpdir.join('baz').write('')
    files = sorted(listdir(None, None, tmpdir.strpath))
    assert len(files) == 2
    assert [os.path.basename(f) for f in files] == ['baz', 'foo']

    out = check_output(None, None, 'ls -l {0}'.format(tmpdir.strpath))
    out_l = [x.split()[-1] for x in out.split('\n') if x.split() and 'rw' in x.split()[0]]
    assert out_l == ['baz', 'foo']

    files = listdir(None, None, tmpdir.strpath, key=lambda x: not x.endswith('baz'))
    assert len(files) == 1
    assert [os.path.basename(f) for f in files] == ['foo']


def test_callback_utility_mkdirp(tmpdir):
    mkdirp = get_callback('mkdirp')
    d = os.path.join(tmpdir.strpath, 'foo', 'baz')
    mkdirp(None, None, d)
    assert os.path.isdir(d)


def test_callback_utility_which():
    which = get_callback('which')
    ls = which(None, None, 'ls')
    assert os.path.exists(ls)


def test_callback_logging(tmpdir, mock_modulepath):
    tmpdir.join('info.py').write('log_info("spam")')
    tmpdir.join('warning.py').write('log_warning("spam")')
    tmpdir.join('error.py').write('log_error("spam")')
    mock_modulepath(tmpdir.strpath)
    pymod.mc.load('info')
    pymod.mc.load('warning')
    try:
        pymod.mc.show('error')
        assert False, 'Should have died'
    except:
        pass