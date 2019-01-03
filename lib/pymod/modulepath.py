import os
import re
import sys
import json

from .cfg import cfg
from .trace import trace
from .color import colorize
from .logging import logging
from .module2 import create_module_from_file, create_module_from_kwds
from .utils import strip_quotes, get_console_dims, wrap2, grep_pat_in_string

if sys.version_info < (2, 7):
    # Python < 2.7 doesn't have the cmp_to_key function.
    from .utils import cmp_to_key
else:
    from functools import cmp_to_key


def compare_module_versions(a, b):
    if a.version is None and b.version is not None:
        return -1
    if a.version is None and b.version is None:
        return 0
    if a.version is not None and b.version is None:
        return 1
    try:
        a.version_tuple < b.version_tuple
        av, bv = a.version_tuple, b.version_tuple
    except TypeError:
        av, bv = a.version, b.version
    if av < bv:
        return -1
    elif av == bv:
        return 0
    return 1


class Modulepath:
    def __init__(self, directories):
        self.path = []
        for directory in directories:
            if not os.access(directory, os.R_OK):
                continue
            if not os.path.isdir(directory):
                logging.warning('Modulepath: nonexistent directory '
                             '{0!r}'.format(directory), minverbosity=2)
            else:
                self.path.append(directory)
        self.modules = None
        self.grouped_by_name = None
        self._cache = self.read_cache()
        self.discover_modules_on_path()

    def __iter__(self):
        for directory in self.path:
            yield (directory, self.modules[directory])

    def __contains__(self, path):
        return path in self.path

    @trace
    def reset(self, directories=None):
        self.modules = None
        self.grouped_by_name = None
        if directories is not None:
            for directory in directories:
                if not os.access(directory, os.R_OK):
                    continue
                if not os.path.isdir(directory):
                    logging.warning('Modulepath: nonexistent directory '
                                 '{0!r}'.format(directory), minverbosity=2)
                else:
                    self.path.append(directory)
        self.discover_modules_on_path()

    @trace
    def get_module_by_name(self, name):
        modules = self.grouped_by_name.get(name)
        if modules is not None:
            return modules[0]
        candidates = {}
        for (directory, modules) in self:
            for module in modules:
                if module.fullname == name:
                    return module
                if os.path.sep in name:
                    # a more qualified path?
                    root = os.path.join(module.modulepath, module.fullname)
                    if root.endswith(name):
                        # store just the length of the intersection of root and key
                        key = len(root.replace(name, ''))
                        if key not in candidates:
                            candidates[key] = module
        if not cfg.strict_modulename_matching and candidates:
            key = min(list(candidates.keys()))
            return candidates[key]
        return None

    @trace
    def get_module_by_filename(self, filename):
        for (directory, modules) in self:
            for module in modules:
                if module.filename == filename:
                    return module
        return None

    @trace
    def sort_and_assign_defaults(self):
        """Assign defaults to modules.  Given a module with multiple versions,
        the default is the module with the highest version across all modules,
        unless explicitly made the default.  A module is explicitly made the
        default by creating a symlink to it (in the same directory) named
        'default'"""
        for (name, modules) in self.grouped_by_name.items():

            for module in modules:
                module.reset_default_status()

            if len(modules) == 1:
                continue

            modules = sorted(modules, key=cmp_to_key(compare_module_versions))
            version_groups = [[modules[0]]]
            for module in modules[1:]:
                if compare_module_versions(module, version_groups[-1][-1]) == 1:
                    version_groups.append([module])
                else:
                    version_groups[-1].append(module)
            modules = [x for y in reversed(version_groups) for x in y]
            span = list(set([x.modulepath for x in modules]))

            default = modules[0]
            for module in modules:
                module.is_default = False

            for (i, module) in enumerate(modules):
                if module.is_explicit_default:
                    break
            else:
                i = 0
            default = modules.pop(i)
            modules.insert(0, default)
            modules[0].is_default = True
            self.grouped_by_name[name] = modules

        return None

    @trace
    def discover_modules_on_path(self):
        self.modules = {}
        self.grouped_by_name = {}
        for directory in self.path:
            modules_in_directory = self.discover_modules_in_directory(directory)
            if modules_in_directory is None:
                logging.warning('Modulepath: no modules found in '
                                '{0}'.format(directory), minverbosity=2)
                continue
            self.modules[directory] = modules_in_directory
            for module in modules_in_directory:
                self.grouped_by_name.setdefault(module.name, []).append(module)
        self.sort_and_assign_defaults()
        return None

    @trace
    def find_linked_default(self, dirname, files):
        name = 'default'
        try:
            files.remove(name)
        except ValueError:
            return None

        path = os.path.join(dirname, name)
        if not os.path.islink(path):
            logging.warning('Modulepath: expected file named default '
                            'in {0} to be a link to a modulefile'.format(dirname),
                            minverbosity=2)
            return None

        source = os.path.realpath(path)
        if os.path.dirname(source) != dirname:
            logging.warning('Modulepath: expected file named default in {0} to be '
                            'a link to a modulefile in the same directory'.format(dirname),
                            minverbosity=2)
            return None

        return source

    @trace
    def find_versioned_default(self, dirname, files):
        # Support for TCL modules .version scheme
        name = '.version'
        try:
            files.remove(name)
        except ValueError:
            return None

        default = None
        path = os.path.join(dirname, name)
        try:
            lines = open(path).readlines()
            regex = """(?i)^\s*set\s+ModulesVersion"""
            for line in lines:
                if " ".join(line.split()).startswith('set ModulesVersion'):
                    tmp = line.split("#", 1)[0].split()[-1]
                    version = strip_quotes(tmp)
                    default = os.path.join(dirname, version)
                    break
            if default is None:
                logging.warning('Could not determine .version default '
                                'in {0}'.format(dirname), minverbosity=2)
            elif not os.path.exists(default):
                logging.warning('{0!r}: versioned default does not '
                                'exist'.format(default), minverbosity=2)
            else:
                return default
        except:
            logging.warning('Could not read {0}'.format(path), minverbosity=2)

        return None

    @trace
    def discover_modules_in_directory(self, directory):
        if not os.access(directory, os.R_OK):
            return None
        if directory == '/':
            raise Exception('Searching root file system!')
        if not os.path.isdir(directory):
            return None

        d_cache = self._cache.get(directory)
        modules = []
        for (dirname, _, files) in os.walk(directory):

            if d_cache:
                for filename in [f for f in files]:
                    path = os.path.join(dirname, filename)
                    try:
                        m_cache = d_cache[path]
                    except KeyError:
                        pass
                    else:
                        if os.stat(path).st_mtime <= m_cache['st_mtime']:
                            modules.append(create_module_from_kwds(**m_cache['kwds']))
                            files.remove(filename)

            if not files:
                continue

            # Determine if there is an explicit default
            linked_default = self.find_linked_default(dirname, files)
            versioned_default = self.find_versioned_default(dirname, files)
            if linked_default and versioned_default:
                logging.warning('A linked and versioned default exist for {0}, '
                                'choosing the linked'.format(os.path.basename(dirname)),
                                minverbosity=2)
                default = linked_default
            else:
                default = linked_default or versioned_default

            # Look for modules
            for filename in files:
                path = os.path.join(dirname, filename)
                is_explicit_default = default == path
                module = create_module_from_file(directory, path, is_explicit_default)
                if module is not None:
                    modules.append(module)
        return sorted(modules, key=lambda x: x.fullname)

    @trace
    def append(self, directory):
        if directory in self.path:
            return None
        if os.path.realpath(directory) in self.path:
            return None
        modules_in_directory = self.discover_modules_in_directory(directory)
        if modules_in_directory is None:
            logging.warning('Modulepath: no modules found in '
                            '{0}'.format(directory), minverbosity=2)
            return None
        self.path.append(directory)
        self.modules[directory] = modules_in_directory

        # Add the new modules to their groups and reassign defaults
        for module in modules_in_directory:
            self.grouped_by_name.setdefault(module.name, []).append(module)
        self.sort_and_assign_defaults()
        return None

    @trace
    def remove(self, directory):
        # Remove the directory from path and associated modules
        if directory in self.path:
            self.path.remove(directory)
            removed = self.modules.pop(directory)
        elif os.path.realpath(directory) in self.path:
            self.path.remove(os.path.realpath(directory))
            removed = self.modules.pop(os.path.realpath(directory))
        else:
            return None

        # Regroup modules and reassign defaults
        self.group_modules_by_name()
        self.sort_and_assign_defaults()
        return removed

    @trace
    def prepend(self, directory):
        if directory in self.path:
            return None
        if os.path.realpath(directory) in self.path:
            return None
        modules_in_directory = self.discover_modules_in_directory(directory)
        if modules_in_directory is None:
            logging.warning('Modulepath: no modules found in '
                            '{0}'.format(directory), minverbosity=2)
            return None
        self.path.insert(0, directory)
        fullnames = [m.fullname for m in modules_in_directory]
        self.modules[directory] = modules_in_directory

        # Find modules that were bumped.  Only bump modules that have the same
        # name/version
        bumped = []
        for other in self.path[1:]:
            for module in self.modules[other]:
                if module.fullname in fullnames:
                    bumped.append(module)

        # Regroup modules and reassign defaults
        self.group_modules_by_name()
        self.sort_and_assign_defaults()
        return bumped

    def group_modules_by_name(self):
        self.grouped_by_name = {}
        for (directory, modules) in self:
            for module in modules:
                self.grouped_by_name.setdefault(module.name, []).append(module)

    def pretty_print(self):
        for d in self.path:
            print(d)
            for m in self.modules[d]:
                print('\t{0}'.format(m))

    def join(self):
        return os.pathsep.join(self.path)

    def available(self):
        return [(d, modules) for (d, modules) in self]

    def filter_modules_by_regex(self, modules, regex):
        if regex:
            modules = [m for m in modules if re.search(regex, m.name)]
        return modules

    def colorize(self, string):
        """Colorize item for output to console"""
        D = '(' + colorize('D', 'green') + ')'
        L = '(' + colorize('L', 'magenta') + ')'
        DL = '(' + colorize('D', 'green') + ',' + colorize('L', 'magenta') + ')'
        colorized = string.replace('(D)', D)
        colorized = colorized.replace('(L)', L)
        colorized = colorized.replace('(D,L)', DL)
        return colorized

    @trace
    def describe(self, terse=False, regex=None, fulloutput=False, pathonly=False):
        if pathonly:
            return '\n'.join('{0}) {1}'.format(i,_[0]) for i,_ in enumerate(self, start=1))

        description = []
        if not terse:
            _, width = get_console_dims()
            for (directory, modules) in self:
                modules = [m for m in modules if m.is_enabled]
                modules = self.filter_modules_by_regex(modules, regex)
                if not os.path.isdir(directory):
                    if not fulloutput:
                        continue
                    s = '(Directory does not exist)'.center(width)
                    s = colorize(s, 'red')
                elif not modules:
                    if not fulloutput:
                        continue
                    s = colorize('(None)'.center(width), 'red')
                else:
                    s = wrap2([m.describe() for m in modules], width)
                    s = self.colorize(s)
                directory = directory.replace(os.path.expanduser('~/'), '~/')
                description.append((' ' + directory + ' ').center(width, '-'))
                description.append(s + '\n')
        else:
            for (directory, modules) in self:
                if not os.path.isdir(directory):
                    continue
                modules = self.filter_modules_by_regex(modules, regex)
                if not modules:
                    continue
                description.append(directory + ':')
                description.append('\n'.join(m.fullname for m in modules))
            description.append('')

        description = '\n'.join(description)
        if regex is not None:
            description = grep_pat_in_string(description, regex)

        return description

    @trace
    def apply(self, fun):
        for (directory, modules) in self:
            for module in modules:
                fun(module)

    @trace
    def candidates(self, key):
        # Return a list of modules that might by given by key
        the_candidates = set()
        regex = re.compile(key)
        for (directory, modules) in self:
            if not modules:
                continue
            for module in modules:
                if regex.search(module.filename):
                    the_candidates.add(module.fullname)
                elif regex.search(module.name) and module.is_default:
                    the_candidates.add(module.fullname)
                elif regex.search(module.fullname):
                    the_candidates.add(module.fullname)
        return sorted(list(the_candidates))

    @trace
    def cache(self, env):
        cache = {}
        for (directory, modules) in self:
            d_cache = {}
            for module in modules:
                t = os.stat(module.filename).st_mtime
                d_cache[module.filename] = {'st_mtime': int(t),
                                            'kwds': module.asdict('load', env)}
            cache[directory] = d_cache
        filename = os.path.join(cfg.dot_dir, 'modulepath.json')
        with open(filename, 'w') as fh:
            json.dump(cache, fh, indent=2)

    @trace
    def read_cache(self):
        filename = os.path.join(cfg.dot_dir, 'modulepath.json')
        if os.path.isfile(filename):
            with open(filename, 'r') as fh:
                return json.load(fh)
        else:
            return {}
