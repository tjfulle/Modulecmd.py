from argparse import ArgumentParser, SUPPRESS


class ModuleArgumentParser(ArgumentParser):

    def __init__(self):
        superinit = super(ModuleArgumentParser, self).__init__
        superinit(prefix_chars='+', add_help=False, usage=SUPPRESS)
        self._argv = None
        self._parsed_argv = None

    def parse_args(self, argv=None):
        argv = argv or []
        superparser = super(ModuleArgumentParser, self).parse_args
        return superparser(argv)

    def add_argument(self, *args, **kwargs):
        chars = self.prefix_chars
        action = kwargs.get('action')
        accepted_actions = (None, 'store', 'store_true', 'store_false')
        if action not in accepted_actions:
            raise ValueError('action must be one of {}'.format(accepted_actions))
        for arg in args:
            if arg[0] not in chars:
                raise ValueError('Positional module arguments not supported')
        superadd = super(ModuleArgumentParser, self).add_argument
        superadd(*args, **kwargs)

    def help_string(self):
        if not self._actions:
            return ''
        help_string = self.format_help()
        description = help_string.replace(
            'optional arguments', 'Module options')
        return description
