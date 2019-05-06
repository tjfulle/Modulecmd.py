import os
import sys
import json
from six import StringIO
from contrib.ordereddict_backport import OrderedDict
import pymod.names
import pymod.environ
import contrib.util.logging as logging
from contrib.util.logging import terminal_size
from contrib.util.logging.colify import colified

"""Manages a collection of modules"""

class Collections:

    def __init__(self, filename):
        self.filename = filename
        self.collections = self.read(filename)

    def __contains__(self, collection_name):
        return collection_name in self.collections

    @staticmethod
    def read(filename):
        if os.path.isfile(filename):
            return OrderedDict(json.load(open(filename)))
        return OrderedDict()

    def write(self, obj, filename):
        if pymod.config.get('dryrun'):
            sys.stderr.write(json.dumps(obj))
        else:
            with open(filename, 'w') as fh:
                json.dump(obj, fh, indent=2)
        return

    def save(self, name, modules, local=False):
        collection = OrderedDict()
        for module in modules:
            m_desc = [module.fullname, module.filename, module.opts]
            collection.setdefault(module.modulepath, []).append(m_desc)
        collection = list(collection.items())
        if local:
            self.write({'collection': collection},
                       filename=name+'.collection')
        else:
            self.collections.update({name: collection})
            self.write(self.collections, self.filename)
        return None

    def get(self, name):
        collection = None
        if os.path.isfile(name):
            collection = self.read(name).get('collection')
        elif os.path.isfile(name+'.collection'):
            collection = self.read(name+'.collection').get('collection')
        else:
            collection = self.collections.get(name)
        return collection

    def remove(self, collection):
        self.collections.pop(name, None)
        self.write(self.collections, self.filename)

    def filter_collections_by_regex(self, collections, regex):
        if regex:
            collections = [c for c in collections if re.search(regex, c)]
        return collections

    def format_available(self, terse=False, regex=None):
        skip = (pymod.names.default_user_collection,
                pymod.names.default_sys_collection)
        names = sorted([x for x in self.collections if x not in skip])

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
            sio.write('{}\n{}\n'
                      .format(' Saved collections '.center(width, '-'), s))
        elif names:
            sio.write('\n'.join(c for c in names))
        string = sio.getvalue()
        if regex is not None:
            string = misc.grep_pat_in_string(string, regex)
        return string

    def format_show(self, name):
        """Show the high-level commands executed by

            module show <collection>
        """
        collection = self.get(name)
        if collection is None:
            logging.warning('{0!r} is not a collection'.format(name))
            return

        sio = StringIO()
        loaded_modules = pymod.environ.get_path(pymod.names.loaded_modules)
        for m in loaded_modules[::-1]:
            sio.write('unload({0!r})\n'.format(m))

        for (directory, modules) in collection:
            sio.write('use({0!r})\n'.format(directory))
            for (name, _, opts) in modules:
                if opts:
                    s = 'load({0!r}, options={1!r})'.format(name, opts)
                else:
                    s = 'load({0!r})'.format(name)
                sio.write(s + '\n')

        return sio.getvalue()
