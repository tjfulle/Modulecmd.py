from enum_backport import Enum

class Modes(Enum):
    NULL = 0
    LOAD = 1
    UNLOAD = 2
    WHATIS = 3
    HELP = 4
    SHOW = 5


null = Modes.NULL
load = Modes.LOAD
unload = Modes.UNLOAD
whatis = Modes.WHATIS
help = Modes.HELP
show = Modes.SHOW


def assert_known_mode(mode):
    assert mode in (null, load, unload, whatis, help, show)


def as_string(mode):
    mapping = {
        null: 'null',
        load: 'load',
        unload: 'unload',
        whatis: 'whatis',
        help: 'help',
        show: 'show'
    }
    return mapping[mode]
