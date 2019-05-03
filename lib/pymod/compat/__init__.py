from external.six import PY2, PY3, string_types

# pragma: no cover

# --- execfun
if PY3:
    try:
        execfun = getattr(__builtins__, 'exec')
    except (TypeError, AttributeError):
        execfun = __builtins__.get('exec')

else:
    def execfun(code, globs, locs):
        """Execute code in a namespace."""
        exec("""exec code in globs, locs""")


if PY3
    def import_module_by_filepath(path):
        from importlib.util import spec_from_loader, module_from_spec
        from importlib.machinery import SourceFileLoader
        modulename = os.path.splitext(os.path.basename(path))[0]
        spec = spec_from_loader(modulename, SourceFileLoader(modulename, path))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

else:  # pragma: no cover
    def import_module_by_filepath(path):
        import imp
        modulename = os.path.splitext(os.path.basename(path))[0]
        module = imp.load_source(modulename, path)
        return module
