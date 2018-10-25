import os
import sys

PYMOD_VERSION = (1, 1, 2)
version = '.'.join('{0}'.format(x) for x in PYMOD_VERSION)

__D = os.path.dirname(os.path.realpath(__file__))
PYMOD_DIR = os.path.realpath(os.path.join(__D, '../..'))
assert os.path.isfile(os.path.join(PYMOD_DIR, '.pymod'))
PYMOD_PKG_DIR = os.path.join(PYMOD_DIR, 'lib/pymod')
assert os.path.isdir(PYMOD_PKG_DIR)

# --------------------------------------------------------------------------- #
# --------------------------- GLOBAL CONSTANTS ------------------------------ #
# --------------------------------------------------------------------------- #
ALIAS, APPEND, AVAIL, CACHE, CAT = 'alias', 'append', 'avail', 'cache', 'cat'
COLLECTION, EDIT, ENV, FILE, HELP = 'collection', 'edit', 'env', 'file', 'help'
INIT, LIST, LOAD, MORE, NULLOP = 'init', 'list', 'load', 'more', '<>'
PREPEND, PURGE, REFRESH, RELOAD = 'prepend', 'purge', 'refresh', 'reload'
REMOVE, RESTORE, RM, SAVE, SHELL = 'remove', 'restore', 'rm', 'save', 'shell'
SHOW, SWAP, UNLOAD, UNUSE, USE = 'show', 'swap', 'unload', 'unuse', 'use'
WHATIS, WHICH, LOAD_FROM_FILE, CLONE = 'whatis', 'which', 'loadfile', 'clone'
TEST, POP = 'test', 'pop'

PLATFORM = sys.platform.lower()
IS_DARWIN = 'darwin' in PLATFORM

MODULE_OPTION_PREFIX = '+'

M_TCL = 'TCL'
M_PY = 'PYTHON'
