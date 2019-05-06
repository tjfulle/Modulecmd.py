import pymod.paths
import pymod.modulepath


def get_entity_text(name):
    module = pymod.modulepath.get(name)
    if module is not None:
        return open(module.filename).read()
    elif name in pymod.collections:
        collection = pymod.collections.get(name)
        return json.dumps(collection, default=serialize, indent=2)
    elif os.path.isfile(os.path.join(pymod.paths.dot_dir, name + '.json')):
        return open(os.path.join(cfg.dot_dir, name + '.json')).read()
    raise Exception('Unknown named entity {0!r}'.format(name))
