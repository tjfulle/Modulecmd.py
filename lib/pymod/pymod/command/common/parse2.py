import os
import re
import ast

tokens = ('@', '%', '^')

def parse(args):

    modules = []
    args = [x for arg in args for x in split_on_tokens(arg)]

    level = None
    prev_tok = None
    module = {}
    i = 0
    while i < len(args):
        arg = args[i]
        next_arg = None if i > len(args) - 2 else args[i+1]
        if arg in tokens:
            prev_tok = arg
            if not module:
                raise ValueError('Module options must follow module name')
            if not next_arg:
                raise ValueError('Expected entries to follow token {0}'.format(arg))
        else:
            if prev_tok == '@':
                prefix = '' if not level else level + '_'
                if module.get(prefix + 'version') is not None:
                    raise ValueError('Duplicate version entry {0}: {1}'
                                     .format(prefix, arg))
                x = arg.split(os.path.sep)
                if len(x) == 1:
                    version, variant = x[0], None
                elif len(x) == 2:
                    version, variant = x[0], x[1]
                else:
                    raise ValueError('Two many path seperators in version {0}'
                                     .format(arg))

                module[prefix + 'version'] = version
                module[prefix + 'variant'] = variant
            elif prev_tok == '%':
                module['compiler_vendor'] = arg
                level = 'compiler'
            elif prev_tok == '^':
                module['mpi_vendor'] = arg
                level = 'mpi'
            else:
                # No previous token, must be an option or a new module
                if is_option(arg):
                    if not module:
                        raise ValueError('Module options must follow module name')
                    opt, val = parse_item_for_module_option(arg)
                    module.setdefault('opts', {}).update({opt: val})
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
                    level = None

            prev_tok = None
        i += 1

    return modules


def split_on_tokens(expr):
    if not expr:  # pragma: no cover
        return []
    split = ['']
    for s in expr:
        if s not in tokens:
            split[-1] = split[-1] + s
        else:
            split.append(s)
            split.append('')
    return [x.strip() for x in split if x.split()]


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
        except (ValueError, SyntaxError):
            pass
    return opt, val


def is_option(item):
    return item.startswith(('+', '-', '~')) or '=' in item[1:]


class IllFormedModuleOptionError(Exception):
    pass


def run(): # pragma: no cover
    keys = ('name', 'version', 'variant',
            'compiler_vendor', 'compiler_version', 'compiler_variant',
            'mpi_vendor', 'mpi_version', 'mpi_variant',
            'opts')
    args =['foo@6.0', '+spam', '-baz', '%gcc@8.3.0', '^openmpi@3.1.2',
           'baz', '@2', 'opt=True', 'foo=x', '~x',
           'bar/4.3.9']
    modules = parse(args)
    for module in modules:
        for key in keys:
            value = module.get(key)
            if value is None:
                continue
            sp = '' if key == 'name' else '  '
            print('{0}{1}: {2}'.format(sp, key, value))
    print('')


if __name__ == "__main__": # pragma: no cover
    run()
