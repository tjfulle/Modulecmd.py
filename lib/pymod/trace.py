import os
from functools import wraps, partial

__trace__ = {}
def trace(fun=None, name=None):
    # Wrapper method to designate which functions to trace when verbosity is set
    # > 2
    if fun is None:
        return partial(trace, name=name)
    __trace__[fun.__name__] = name or fun.__name__
    @wraps(fun)
    def inner(*args, **kwargs):
        return fun(*args, **kwargs)
    return inner


def trace_function(func):
    __trace__[func.__name__] = func.__name__


def get_classname_from_frame(frame):
    import inspect
    args, _, _, value_dict = inspect.getargvalues(frame)
    # we check the first parameter for the frame function is named 'self'.  If
    # so, we *assume* it is a class method.  Though, in this file, only class
    # methods have the first parameter named 'self'.
    if len(args) and args[0] == 'self':
        instance = value_dict.get('self', None)
        if instance:
          return instance.__class__.__name__
    return None


def trace_calls(frame, event, arg, level=[-1]):  # pragma: no cover
    """Function used to trace calls through modulecmd

    If the global verbosity is > 2, then this function is passed to sys.settrace
    to track paths through modulecmd.  With all of the callback functions and
    exec'ing module files, the code paths can be surprisingly convoluted.

    """
    def string_repr(item):
        if isinstance(item, (dict, OrderedDict)):
            if not item:
                return '{}'
            keys = sorted(item.keys())
            k1, k2 = keys[0], keys[-1]
            v1, v2 = item[k1], item[k2]
            return '{{{0!r}={1!r}, ..., {2!r}: {3!r}}}'.format(k1, v1, k2, v2)
        elif isinstance(item, (tuple, list)):
            if not item:
                return '[]'
            return '[{0!r}, ..., {1!r}]'.format(item[0], item[-1])
        else:
            return '{0!r}'.format(item)

    try:
        basename = os.path.basename('')
    except (AttributeError, TypeError):
        return

    co = frame.f_code
    if os.path.basename(co.co_filename) != 'modulecmd.py':
        # Only trace *this* file
        return

    classname = get_classname_from_frame(frame)
    if co.co_name == '__init__':
        kc = ['Module2', 'MasterController', 'AvailableModules2']
        if classname not in kc:
            return
        funcname = classname

    else:
        funcname = __trace__.get(co.co_name)
        if funcname is None:
            return
        if classname is not None:
            funcname = '{0}.{1}'.format(classname, funcname)

    if event == 'return':
        level[0] -= 1
        return

    if event == 'call':

        func_lineno = frame.f_lineno

        level[0] += 1
        indent = '  ' * level[0]

        func_args = []
        for i in range(co.co_argcount):
            arg = co.co_varnames[i]
            if arg == 'self':
                continue
            val = string_repr(frame.f_locals[arg])
            func_args.append('{0}={1}'.format(arg, val))

        line = '{0}{1}({2})'.format(indent, funcname, ', '.join(func_args))
        write_to_console(line, 3)

        return trace_calls

    return


