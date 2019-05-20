import pymod.paths
import pymod.error
import pymod.modulepath
import pymod.collection
from contrib.util.tty.pager import pager


def get_entity_text(name):
    module = pymod.modulepath.get(name)
    if module is not None:
        return open(module.filename).read()
    elif pymod.collection.contains(name):
        return str(pymod.collection.get(name))
    raise pymod.error.EntityNotFoundError(name)


def more(name):
    pager(get_entity_text(name))


def cat(name):
    pager(get_entity_text(name), plain=True)
