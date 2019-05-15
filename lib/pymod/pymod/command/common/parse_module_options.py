def parse_module_options(args):
    # To pass arguments to a module, do
    #
    #  module <subcommand> module +option[=value]...
    #
    argv = []
    args = args or []
    for item in args:
        if item.startswith('+'):
            if not argv:
                raise ValueError('Options must be specified after module name')
            argv[-1][-1].append(item)
        else:
            argv.append((item, []))
    return argv
