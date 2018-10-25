import re
from functools import wraps

from .logging import write_to_console
from .trace import trace_function
from .utils import get_console_dims


# --------------------------------------------------------------------------- #
# ---------------------------- INSTRUCTION LOGGER --------------------------- #
# --------------------------------------------------------------------------- #
class InstructionLogger(object):  # pragma: no cover
    """Class that logs instructions"""
    instructions = [[(None, None)]]

    @classmethod
    def start_new_instructions(klass, name, filename):
        klass.instructions.append([(name, filename)])

    @classmethod
    def append(klass, arg):
        klass.instructions[-1].append(arg)

    @classmethod
    def log_instruction(klass, func):
        trace_function(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            p = ', '.join('{0!r}'.format(str(x)) for x in args[1:])
            if kwargs:
                s = ['{0}={1!r}'.format(*x) for x in kwargs.items()]
                p += ', ' + ', '.join(s)
            s = '{0}({1})'.format(func.__name__, p)
            klass.instructions[-1].append(s)
            return func(*args, **kwargs)
        return wrapper

    @classmethod
    def show(klass):
        regex = re.compile(r'^(?m)(unload|load|family).*(\n|$)')
        try:
            _, width = get_console_dims()
        except ValueError:
            width = 80
        header = '-'*width + '\n'
        for instructions in klass.instructions:
            name, filename = instructions[0]
            if name is None:
                continue
            string = '\n'.join(instructions[1:])
            if regex.search(string):
                string = regex.sub('', string)
            if not string.split():
                continue
            write_to_console(string, 0, end='\n')

    @classmethod
    def append_collection_instructions(klass, collection, path, instructions):
        klass.instructions.append([(collection, path)])
        klass.instructions[-1].extend(instructions)
