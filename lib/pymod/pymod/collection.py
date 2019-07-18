import os
import re
import sys
import json
from six import StringIO
from ordereddict_backport import OrderedDict

import pymod.names
import pymod.paths
import pymod.compat
import pymod.environ

import llnl.util.tty as tty
from llnl.util.tty import terminal_size
from llnl.util.tty.colify import colified
from llnl.util.lang import Singleton


class Collections:
    """Manages a collection of modules"""
    version = (1, 0)
    def __init__(self, filename):
        self.filename = filename
        self.data = self.read(filename)

    def __contains__(self, collection_name):
        return collection_name in self.data

    def read(self, filename):
        if os.path.isfile(filename):
            obj = dict(json.load(open(filename)))
            version = obj.get('Version')
            version = version if version is None else tuple(version)
            if version != Collections.version: # pragma: no cover
                return pymod.compat.collection.upgrade(self, obj, version)
            else:
                return dict(obj['Collections'])
        return dict()

    def write(self, collections, filename):
        obj = {'Version': self.version, 'Collections': collections}
        if pymod.config.get('dryrun'):  # pragma: no cover
            sys.stderr.write(json.dumps(obj))
        else:
            with open(filename, 'w') as fh:
                json.dump(obj, fh, indent=2)
        return

    def save(self, name, modules):
        collection = OrderedDict()
        for module in modules:
            ar = pymod.mc.archive_module(module)
            ar['refcount'] = 0
            collection.setdefault(module.modulepath, []).append(ar)
        collection = list(collection.items())
        self.data.update({name: collection})
        self.write(self.data, self.filename)
        return None

    def get(self, name):
        return self.data.get(name)

    def remove(self, name):
        self.data.pop(name, None)
        self.write(self.data, self.filename)

    def filter_collections_by_regex(self, collections, regex):
        if regex:
            collections = [c for c in collections if re.search(regex, c)]
        return collections

    def avail(self, terse=False, regex=None):
        skip = (pymod.names.default_user_collection,)
        names = sorted([x for x in self.data if x not in skip])

        if regex:
            names = self.filter_collections_by_regex(names, regex)

        if not names:  # pragma: no cover
            return ''

        sio = StringIO()
        if not terse:
            _, width = terminal_size()
            s = colified(names, width=width)
            sio.write('{0}\n{1}\n'
                      .format(' Saved collections '.center(width, '-'), s))
        else:
            sio.write('\n'.join(c for c in names))
        string = sio.getvalue()
        return string

    def show(self, name):
        """Show the high-level commands executed by

            module show <collection>
        """
        collection = self.get(name)
        if collection is None: # pragma: no cover
            tty.warning('{0!r} is not a collection'.format(name))
            return

        sio = StringIO()
        loaded_modules = pymod.mc.get_loaded_modules()
        for m in loaded_modules[::-1]:
            sio.write('unload({0!r})\n'.format(m.fullname))

        for (directory, archives) in collection:
            sio.write('use({0!r})\n'.format(directory))
            for ar in archives:
                name = ar['fullname']
                opts = ar['opts']
                if opts:
                    opts_string = pymod.module.Namespace(**opts).joined(' ')
                    s = 'load({0!r}, options={1!r})'.format(name, opts_string)
                else:
                    s = 'load({0!r})'.format(name)
                sio.write(s + '\n')

        return sio.getvalue()


def factory():
    basename = pymod.names.collections_file_basename
    filename = pymod.paths.join_user(basename)
    return Collections(filename)


collections = Singleton(factory)


def save(name, loaded_modules):
    return collections.save(name, loaded_modules)


def remove(name):
    return collections.remove(name)


def get(name):
    return collections.get(name)


def avail(terse=False, regex=None):
    return collections.avail(terse=terse, regex=regex)


def show(name):
    return collections.show(name)


def contains(name):
    return name in collections


def version():
    return Collections.version
