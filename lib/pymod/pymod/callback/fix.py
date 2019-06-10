import os
import re

def sortkey(x):
    xx = x.split('.')
    if len(xx) == 1:
        return (0, x)
    return (len(x), x)

funs = {}
lines = open('foo', 'r').readlines()
fun = None

for line in lines:
    if line.startswith('def '):
        key = line.split()[1]
        i = key.find('(')
        fun = key[:i]
        funs[fun] = [line]
        continue
    if not fun:
        continue
    funs[fun].append(line)

import_re = re.compile('(?m)(\w+)\.(\w+)')
for fun in sorted(funs):
    skip = []
    imports = set()
    content = funs[fun]
    for (first, second) in import_re.findall(''.join(content)):
        if not first.split():
            continue
        if not second.split():
            continue
        if first == 'pymod':
            assert len(second.split())
            imports.add('import {0}.{1}'.format(first, second))
        elif first in ('os', 'sys'):
            imports.add('import {0}'.format(first))
        elif first in ('kwds', 'module', 'other', 'string', 'done', 'loaded', 'MODULEPATH', 'mc', 'unload', 'time', 'environment',
                       'unloaded', 'it', 'order', 'Modulecmd', 'Modulecmd.py', 'swapped', 'version', 'alias', 'function', 'variable',
                       'unconditionally'):
            continue
        else:
            skip.append('{0}.{1}'.format(first, second))

    if skip:
        print('for function {0!r}, skipping:\n\t{1}'.format(fun, '\n\t'.join(skip)))

    imports = sorted(list(imports), key=sortkey)
    if 'ModuleNotFoundError' in ''.join(content):
        imports.append('from pymod.error import ModuleNotFoundError')
    with open('{0}.py'.format(fun), 'w') as fh:
        fh.write('\n'.join(imports))
        fh.write('\n\n')
        fh.write("category = ''\n")
        fh.write('\n\n')
        fh.write(''.join(funs[fun]).strip())

