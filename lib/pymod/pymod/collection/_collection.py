import os
import re
import sys
import json
from six import StringIO
from ordereddict_backport import OrderedDict
import pymod.names
import pymod.environ
import llnl.util.tty as tty
from llnl.util.tty import terminal_size
from llnl.util.tty.colify import colified

"""Manages a collection of modules"""

class Collections:
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
                return self.upgrade(version, obj)
            else:
                return dict(obj['Collections'])
        return dict()

    def write(self, collections, filename):
        if pymod.config.get('dryrun'):  # pragma: no cover
            sys.stderr.write(json.dumps(obj))
        else:
            obj = {'Version': self.version, 'Collections': collections}
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

    def format_available(self, terse=False, regex=None):
        skip = (pymod.names.default_user_collection,)
        names = sorted([x for x in self.data if x not in skip])

        if regex:
            names = self.filter_collections_by_regex(names, regex)
            if not names:
                return ''

        sio = StringIO()
        if not terse:
            _, width = terminal_size()
            if not names:
                s = '(None)'.center(width)
            else:
                s = colified(names, width=width)
            sio.write('{0}\n{1}\n'
                      .format(' Saved collections '.center(width, '-'), s))
        elif names:
            sio.write('\n'.join(c for c in names))
        string = sio.getvalue()
        return string

    def format_show(self, name):
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
                    s = 'load({0!r}, options={1!r})'.format(name, opts)
                else:
                    s = 'load({0!r})'.format(name)
                sio.write(s + '\n')

        return sio.getvalue()

    def upgrade(self, version, old_collections, depth=[0]):  # pragma: no cover
        import pymod.modulepath
        depth[0] += 1
        if depth[0] > 1:
            raise ValueError('Recursion!')
        if version is None:
            new_collections = {}
            mp = pymod.modulepath.Modulepath([])
            for (name, old_collection) in old_collections.items():
                new_collection = OrderedDict()
                for (path, m_descs) in old_collection:
                    if new_collection is None:
                        break
                    if not os.path.isdir(path):
                        tty.warn(
                            'Collection {0} contains directory {1} which '
                            'does not exist!  This collection will be skipped'
                            .format(name, path))
                        new_collection = None
                        break
                    avail = mp.append_path(path)
                    if avail is None:
                        tty.warn(
                            'Collection {0} contains directory {1} which '
                            'does not have any available modules!  '
                            'This collection will be skipped'
                            .format(name, path))
                        new_collection = None
                        break
                    for (fullname, filename, opts) in m_descs:
                        m = mp.get(filename)
                        if m is None:
                            tty.warn(
                                'Collection {0} requests module {1} which '
                                'can not be found! This collection will be skipped'
                                .format(name, fullname))
                            new_collection = None
                            break
                        m.opts = opts
                        m.acquired_as = m.fullname
                        ar = pymod.mc.archive_module(m)
                        new_collection.setdefault(m.modulepath, []).append(ar)

                if new_collection is None:
                    continue

                new_collections[name] = list(new_collection.items())

            bak = self.filename + '.bak'
            with open(bak, 'w') as fh:
                json.dump(old_collections, fh, indent=2)

            self.write(list(new_collections.items()), self.filename)
            return new_collections

        elif version != self.version:
            raise ValueError('No known conversion from Collections version '
                             '{0} to {1}'.format(version, self.version))
