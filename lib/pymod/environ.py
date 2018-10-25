import os
from collections import OrderedDict

from .defaults import MP_KEY, LM_FILES_KEY, LM_KEY, LM_OPTS_KEY
from .trace import trace
from .utils import split, join, str2dict, dict2str


class Environ(OrderedDict):

    def __init__(self, env):
        super(Environ, self).__init__()
        self.update(env)
        self.ini = dict(env)
        if MP_KEY not in self:
            self[MP_KEY] = None

    def copy(self):
        return dict([item for item in self.items()])

    def defined(self, name):
        val = self.get(name, '').lower()
        if val in ('1', 'on', 'true'):
            return True
        elif val in ('0', 'off', 'false'):
            return False
        return None

    @trace
    def get_loaded_modules(self, what, reverse=False, module=None):
        if what == 'filenames':
            key = LM_FILES_KEY
        elif what == 'names':
            key = LM_KEY
        elif what == 'opts':
            key = LM_OPTS_KEY
        else:
            raise ValueError('what must be filenames, names, or opts')

        lm_entity = self.get(key)

        if what == 'opts':
            if lm_entity is None:
                if module is not None:
                    return None
                return {}
            d = str2dict(lm_entity)
            if module is None:
                return d
            return d.get(module.fullname)

        else:
            lm_entity = split(lm_entity, os.pathsep)
            if reverse:
                return lm_entity[::-1]
            return lm_entity

    @trace
    def set_loaded_modules(self, what, lm_entity):
        """Set the names of the loaded modules to the environment"""
        if what == 'filenames':
            key = LM_FILES_KEY
        elif what == 'names':
            key = LM_KEY
        elif what == 'opts':
            key = LM_OPTS_KEY
        else:
            raise ValueError('what must be filenames, names, or opts')
        if what == 'opts':
            self[LM_OPTS_KEY] = dict2str(lm_entity)
        else:
            self[key] = join(lm_entity, os.pathsep)
