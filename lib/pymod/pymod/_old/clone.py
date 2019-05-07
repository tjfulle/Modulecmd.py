    def read_clones(self, filename):
        if os.path.isfile(filename):
            return dict(json.load(open(filename)))
        return {}

    @trace
    def clone_current_environment(self, name):
        env = self.shell.filter_environ(self.environ)
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        clones[name] = [(key, val) for (key, val) in env.items()]
        with open(filename, 'w') as fh:
            json.dump(clones, fh, default=serialize, indent=2)
        return

    @trace
    def restore_clone(self, name):
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        if name not in clones:
            tty.die('{0!r} is not a cloned environment'.format(name))
        the_clone = dict(clones[name])

        # Purge current environment
        self.purge(allow_load_after_purge=False)
        self.modulepath.reset(directories=the_clone[MP_KEY].split(os.pathsep))

        # Make sure environment matches clone
        for (key, val) in the_clone.items():
            self.environ[key] = val

        # Load modules to make sure aliases/functions are restored
        module_files = split(the_clone[LM_FILES_KEY], os.pathsep)
        module_opts = str2dict(the_clone[LM_OPTS_KEY])

        for (i, filename) in enumerate(module_files):
            module = self.modulepath.get_module_by_filename(filename)
            if module is None:
                raise ModuleNotFoundError(filename, self.modulepath)
            self.set_moduleopts(module, module_opts[module.fullname])
            self.execmodule(LOAD_PARTIAL, module, do_not_register=True)

    @trace
    def remove_clone(self, name):
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        clones.pop(name, None)
        with open(filename, 'w') as fh:
            json.dump(clones, fh, default=serialize, indent=2)
        return

    @trace
    def display_clones(self, terse=False, stream=sys.stderr):
        string = []
        filename = cfg.clones_filename
        clones = self.read_clones(filename)
        names = sorted([x for x in clones.keys()])
        if not terse:
            _, width = get_console_dims()
            if not names:
                s = '(None)'.center(width)
            else:
                s = wrap2(names, width)
            string.append(s+'\n')
        else:
            if names:
                string.append('\n'.join(c for c in names))

        string = '\n'.join(string)
        stream.write(string)
