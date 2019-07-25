import os
import re
import ast

tokens = ('@', '%', '^')

def parse(args):

    modules = []
    args = [x for arg in args for x in split_on_tokens(arg)]

    level = None
    module = {}
    i = 0
    while i < len(args):
        arg = args[i]
        next_arg = None if i > len(args) - 2 else args[i+1]
        if arg in tokens:
            if not module:
                raise ValueError('Module options must follow module name')
            if arg == '%':
                level = 'compiler'
            elif arg == '^':
                level = 'mpi'
            elif arg == '@':
                i += 1  # advance past the '@'
                if next_arg is None:
                    raise ValueError("Expected version string to follow '@'")
                prefix = '' if not level else level + '_'
                if module.get(prefix + 'version') is not None:
                    raise ValueError('Duplicate version entry {0}: {1}'
                                     .format(key, next_arg))
                x = next_arg.split(os.path.sep)
                if len(x) == 1:
                    version, variant = x[0], None
                elif len(x) == 2:
                    version, variant = x[0], x[1]
                else:
                    raise ValueError('Two many path seperators in version {0}'
                                     .format(next_arg))

                module[prefix + 'version'] = version
                module[prefix + 'variant'] = variant
                # Now that we have the version, reset the level
                level = None
        else:
            opt, val = parse_item_for_module_option(arg)
            if opt is not None:
                if not module:
                    raise ValueError('Module options must follow module name')
                module.setdefault('opts', {}).update({opt: val})
            elif level in ('compiler', 'mpi'):
                if not module:
                    raise ValueError('Module hierarchy must follow module name')
                module[level + '_vendor'] = arg
                if next_arg != '@':
                    level = None
            else:
                x = arg.split(os.path.sep)
                if len(x) == 1:
                    name, version, variant = x[0], None, None
                elif len(x) == 2:
                    name, version, variant = x[0], x[1], None
                elif len(x) == 3:
                    name, version, variant = x[0], x[1], x[2]
                else:
                    raise ValueError('Two many path seperators in {0}'
                                     .format(arg))
                module = {'name': name, 'version': version, 'variant': variant}
                modules.append(module)
        i += 1

    return modules


def split_on_tokens(expr):
    if not expr:
        return []
    split = ['']
    for s in expr:
        if s not in tokens:
            split[-1] = split[-1] + s
        else:
            split.append(s)
            split.append('')
    return [x for x in split if x.split()]


def parse_item_for_module_option(item):
    try:
        opt, val = item.split('=', 1)
    except ValueError:
        if not item.startswith(('+', '-', '~')):
            return None, None
        # Possibly an option, make sure it is well formed.
        if len(item) == 1:
            raise IllFormedModuleOptionError(item)
        if item[1] in ('+', '-', '~'):
            raise IllFormedModuleOptionError(item)
        opt = item[1:]
        if not re.search(r'(?i)[a-z_]', opt[0]):
            # Must start with a-z or _
            raise IllFormedModuleOptionError(item)
        val = True if item[0] == '+' else False
    else:
        try:
            val = ast.literal_eval(val)
        except ValueError:
            pass
    return opt, val


class IllFormedModuleOptionError(Exception):
    pass


modules = parse(['foo@3.1.2', '%gcc@8.3.0', '^openmpi@3.1.2', '+spam', '-baz', '~x', 'baz', '@2', 'opt=True', 'foo=x', 'bar/4.3.9'])
for module in modules:
    print(module)
