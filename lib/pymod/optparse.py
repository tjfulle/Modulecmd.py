import re
from copy import deepcopy as copy
from collections import OrderedDict

from .logging import logging
from .constants import *


# --------------------------------------------------------------------------- #
# ------------------- MODULE OPTIONS CLASS ---------------------------------- #
# --------------------------------------------------------------------------- #
class OptionNamespace(object):
    def __init__(self, **kwds):
        for (option_string, opt) in kwds.items():
            setattr(self, opt.dest, opt.value)


class _ModuleOption:
    def __init__(self, option_string, dest, value, action, conflict, helpstr):
        self.option_string = option_string
        self.dest = dest
        self.value = value
        self.action = action
        self.conflict = conflict
        self.helpstr = helpstr

    def set(self, *args):
        if self.action in ('store_true', 'store_false'):
            if len(args) != 0:
                msg = "Option {0} takes no explicit arguments"
                logging.error(msg.format(self.option_string))
            value = True if self.action == 'store_true' else False
        elif self.action == 'store':
            if len(args) != 1:
                msg = "Option {0} requires one explicit argument"
                logging.error(msg.format(self.option_string))
            value = args[0].strip()
        else:
            raise Exception('Bad action')
        self.value = value


class ModuleOptionParser(object):
    """Light-weight specialized parser for module files to provide options"""
    prefix_char = MODULE_OPTION_PREFIX

    def __init__(self):
        self.valid_actions = ('store_true', 'store', 'store_false')
        self.registered_options = OrderedDict()
        self.parsed_options = None

    @classmethod
    def is_valid_option_string(klass, option_spec):
        option_string = option_spec.split('=')[0]
        regex = '(?i)^{0}\w+$'.format(re.escape(klass.prefix_char))
        return bool(re.search(regex, option_string))

    def add_mutually_exclusive_option(self, o1, o2, action='store_true',
                                      help=None):
        self.add_option(o1, conflict=o2, action=action, help=help)
        self.add_option(o2, conflict=o1, action=action, help=help)

    def add_option(self, option_string, action='store_true', conflict=None,
                   help=None):
        """Add option to this parser"""
        if not self.is_valid_option_string(option_string):
            msg = "Expected module option {0!r} to be prefixed by 1 {1!r} "
            msg += "character".format(option_string, self.prefix_char)
            logging.error(msg)
        if action not in self.valid_actions:
            msg = 'action for option {0!r} must be one of {1}'
            s_va = ', '.join(self.valid_actions)
            logging.error(msg.format(option_string, s_va))
        if option_string in self.registered_options:
            msg = 'Duplicate option {0!r}'
            logging.error(msg.format(option_string))
        if conflict is not None and not self.is_valid_option_string(conflict):
            msg = "Expected conflict for option {0!r} "
            msg += "to be prefixed by 1 {1!r} character"
            logging.error(msg.format(option_string, self.prefix_char))
        dest = option_string.lstrip(self.prefix_char)
        opt = _ModuleOption(option_string, dest, None, action, conflict, help)
        self.registered_options[option_string] = opt

    def parse_opts(self, argv):
        argv = argv or []
        self.parsed_options = copy(self.registered_options)
        for arg in argv:
            split_arg = arg.split('=')
            option_string = split_arg[0]
            if option_string not in self.parsed_options:
                msg = '{0!r}: unrecognized option'.format(option_string)
                logging.error(msg)
            opt = self.parsed_options[option_string].set(*split_arg[1:])
        # check for conflicts
        for (option_string, opt) in self.parsed_options.items():
            if opt.conflict is None:
                continue
            if opt.value is None:
                continue
            other = self.parsed_options.get(opt.conflict)
            if other is None:
                continue
            if other.value is not None:
                msg = 'Option {0!r} conflicts with {1!r}'
                logging.error(msg.format(other.option_string, option_string))
        return OptionNamespace(**self.parsed_options)

    def get_set_options(self):
        if self.parsed_options is None:
            return None
        x = []
        for (option_string, opt) in self.parsed_options.items():
            if opt.value is None:
                continue
            if opt.action in ('store_true', 'store_false'):
                x.append(option_string)
            else:
                x.append('{0}={1}'.format(option_string, opt.value))
        if not x:
            return None
        return x

    def description(self):
        n = 0
        for (option_string, opt) in self.registered_options.items():
            if opt.action in ('store_true', 'store_false'):
                n = max(n, len(option_string))
            elif opt.action == 'store':
                s = '{0}={1}'.format(option_string, opt.dest.upper())
                n = max(n, len(s))
        n += 4

        x = ['Module Options:']
        for (option_string, opt) in self.registered_options.items():
            if opt.action in ('store_true', 'store_false'):
                s = option_string
            elif opt.action == 'store':
                s = '{0}={1}'.format(option_string, opt.dest.upper())
            else:
                raise Exception('Bad action')

            helpstr = '' if not opt.helpstr else opt.helpstr + ' '
            if opt.conflict:
                helpstr += '[conflict: {0}]'.format(opt.conflict)
            line = '  {0:<{1}}{2}'.format(s, n, helpstr)
            x.append(line)
        return '\n'.join(x)


