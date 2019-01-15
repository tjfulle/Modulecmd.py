import os
import re
import json
from collections import OrderedDict

from .constants import *
from .trace import trace
from . import defaults
from .utils import serialize, get_console_dims, wrap2, grep_pat_in_string
from .color import colorize
from .logging import logging
from .config import cfg


# --------------------------------------------------------------------------- #
# --------------------------- AVAILABLE MODULES ----------------------------- #
# --------------------------------------------------------------------------- #
class Collections:

    def __init__(self):
        self._items = None

    def __contains__(self, name):
        return name in self.items

    def __setitem__(self, name, collection):
        items = self.items
        items[name] = collection
        self.write(items)

    @trace
    def read(self, filename=None):
        filename = filename or cfg.collections_filename
        if os.path.isfile(filename):
            return json.load(open(filename))
        return {}

    @trace
    def write(self, collections, filename=None):
        filename = filename or cfg.collections_filename
        with open(filename, 'w') as fh:
            json.dump(collections, fh, default=serialize, indent=2)
        return

    @property
    def items(self):
        if self._items is None:
            self._items = self.read()
        return self._items

    @trace
    def save(self, name, modules, module_opts, isolate=False):
        this_collection = OrderedDict()
        for module in modules:
            d = module.asdict()
            d['options'] = module_opts.get(module.fullname) or []
            this_collection.setdefault(module.modulepath, []).append(d)
        this_collection = list(this_collection.items())
        if not isolate:
            items = self.items
            items[name] = this_collection
            self.write(items)
        else:
            self.write({'collection': this_collection},
                       filename=name+'.collection')
        return None

    @trace
    def get(self, name):
        collection = None
        if os.path.isfile(name):
            collection = self.read(name).get('collection')
        else:
            collection = self.items.get(name)
            if collection is None and os.path.isfile(name+'.collection'):
                collection = self.read(name+'.collection').get('collection')
        return collection

    @trace
    def remove(self, name):
        items = self.items
        items.pop(name, None)
        self.write(items)

    def filter_collections_by_regex(self, collections, regex):
        if regex:
            collections = [c for c in collections if re.search(regex, c)]
        return collections

    @trace
    def describe(self, terse=False, regex=None):
        string = []
        items = self.items
        skip = (defaults.DEFAULT_USER_COLLECTION_NAME,
                defaults.DEFAULT_SYS_COLLECTION_NAME)
        names = sorted([x for x in items.keys() if x not in skip])
        if regex:
            names = self.filter_collections_by_regex(names, regex)
            if not names:
                return ''
        if not terse:
            _, width = get_console_dims()
            if not names:
                s = '(None)'.center(width)
            else:
                s = wrap2(names, width)
            string.append(' Saved collections '.center(width, '-'))
            string.append(s+'\n')
        else:
            if names:
                string.append('\n'.join(c for c in names))

        string = '\n'.join(string)
        if regex is not None:
            string = grep_pat_in_string(string, regex)
        return string
