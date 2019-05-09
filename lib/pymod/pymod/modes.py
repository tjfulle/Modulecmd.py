from enum_backport import Enum

class Modes(Enum):
    NULL = 0
    LOAD = 1
    UNLOAD = 2
    WHATIS = 3
    HELP = 4
    SHOW = 5
    LOAD_PARTIAL = 6


null = Modes.NULL
load = Modes.LOAD
unload = Modes.UNLOAD
whatis = Modes.WHATIS
help = Modes.HELP
show = Modes.SHOW
load_partial = Modes.LOAD_PARTIAL


def assert_known_mode(mode):
    assert mode in (null, load, unload, whatis, help, show, load_partial)


_mapping = {
    null: 'null',
    load: 'load',
    unload: 'unload',
    whatis: 'whatis',
    help: 'help',
    show: 'show',
    load_partial: 'load_partial'
}


def as_string(mode):
    return _mapping[mode]


def get_mode(mode):
    for (key, val) in _mapping.items():
        if mode == val:
            return key
    return None
