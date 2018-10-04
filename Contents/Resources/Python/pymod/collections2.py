import os
import re
import json
from collections import OrderedDict

from .constants import *
from .trace import trace
from . import defaults
from .utils import serialize, get_console_dims, wrap2, strip_quotes, grep_pat_in_string
from .color import colorize
from .logging import logging


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
    def read(self):
        filename = defaults.collections_filename()
        if os.path.isfile(filename):
            return json.load(open(filename))
        return {}

    @trace
    def write(self, collections):
        filename = defaults.collections_filename()
        with open(filename, 'w') as fh:
            json.dump(collections, fh, default=serialize, indent=2)
        return

    @property
    def items(self):
        if self._items is None:
            self._items = self.read()
        return self._items

    @trace
    def save(self, name, modules, module_opts):
        this_collection = OrderedDict()
        for module in modules:
            d = module.asdict()
            d['options'] = module_opts.get(module.fullname) or []
            this_collection.setdefault(module.modulepath, []).append(d)
        items = self.items
        items[name] = list(this_collection.items())
        self.write(items)
        return None

    @trace
    def get(self, name):
        return self.items.get(name)

    @trace
    def remove(self, name):
        items = self.items
        items.pop(name, None)
        self.write(items)

    @trace
    def describe(self, terse=False):
        string = []
        items = self.items
        skip = (defaults.DEFAULT_USER_COLLECTION_NAME,
                defaults.DEFAULT_SYS_COLLECTION_NAME)
        names = sorted([x for x in items.keys() if x not in skip])
        if not terse:
            _, width = get_console_dims()
            if not names:
                s = '(None)'.center(width)
            else:
                s = wrap2(names, width)
            string.append(s+'\n')
        else:
            if names:
                string.append('\n'.join(c for c in names))

        string = '\n'.join(string)
        return string
