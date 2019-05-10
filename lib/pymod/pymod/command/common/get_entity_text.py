import pymod.paths
import pymod.modulepath
import pymod.collection


def get_entity_text(name):
    module = pymod.modulepath.get(name)
    if module is not None:
        return open(module.filename).read()
    elif pymod.collection.contains(name):
        return str(pymod.collection.get(name))
    raise Exception('Unknown named entity {0!r}'.format(name))
