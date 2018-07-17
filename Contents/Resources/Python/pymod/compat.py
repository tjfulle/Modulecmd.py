import os
import sys

# Python 2,3 compatibility
if sys.version_info[0] == 3:  # pragma: no cover
    string_types = str, bytes
    try:
        execfun = getattr(__builtins__, 'exec')
    except (TypeError, AttributeError):
        execfun = __builtins__.get('exec')

    def import_module_by_filepath(path):
        from importlib.util import spec_from_loader, module_from_spec
        from importlib.machinery import SourceFileLoader
        modulename = os.path.splitext(os.path.basename(path))[0]
        spec = spec_from_loader(modulename, SourceFileLoader(modulename, path))
        foo = module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo

else:  # pragma: no cover
    string_types = basestring,

    def execfun(code, globs, locs):
        """Execute code in a namespace."""
        exec("""exec code in globs, locs""")

    def import_module_by_filepath(path):
        import imp
        modulename = os.path.splitext(os.path.basename(path))[0]
        return imp.load_source(modulename, path)
