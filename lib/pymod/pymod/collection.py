
    @trace
    def save_collection(self, name, isolate=False):
        loaded = self.get_loaded_modules()
        module_opts = self.environ.get_loaded_modules('opts')
        self.collections.save(name, loaded, module_opts, isolate=isolate)

    @trace
    def remove_collection(self, name):
        self.collections.remove(name)

    @trace
    def restore_collection(self, name, warn_if_missing=True):

        if name == 'system':
            name = DEFAULT_SYS_COLLECTION_NAME

        collection = self.collections.get(name)
        if collection is None:
            if warn_if_missing:
                if name == DEFAULT_SYS_COLLECTION_NAME:
                    msg = 'System default collection does not exist'
                else:
                    msg = 'Collection {0!r} does not exist'.format(name)
                logging.warning(msg)
            return None

        # First unload all loaded modules
        loaded = self.get_loaded_modules(reverse=True)
        for module in loaded:
            self.execmodule(UNLOAD, module)

        # Now load the collection, one module at a time
        for (directory, modules) in collection:
            self.use(directory, append=True)
            for m_dict in modules:
                module = self.modulepath.get_module_by_filename(m_dict['filename'])
                if module is None:
                    msg = 'Saved module {0!r} does not exist ({1})'.format(m_dict['name'], m_dict['filename'])
                    if cfg.stop_on_error:
                        logging.error(msg)
                    else:
                        logging.warning(msg)
                        continue
                if m_dict['options']:
                    self.set_moduleopts(module, m_dict['options'])
                self.execmodule(LOAD, module)
        return None

    @trace
    def restore(self, name, warn_if_missing=True):
        self.restore_collection(name, warn_if_missing=warn_if_missing)

    @trace
    def edit_collection(self, name):  # pragma: no cover
        """Edit the collection"""
        import tempfile
        from subprocess import call
        collection = self.collections.get(name)
        if collection is None:
            logging.warning('{0!r} is not a collection'.format(name))
            return
        snew = edit_string_in_vim(json.dumps(collection, default=serialize, indent=2))
        self.collections[name] = json.loads(snew)

    @trace
    def show_available_collections(self, terse=False, regex=None,
                                   stream=sys.stderr):
        s = self.collections.describe(terse=terse, regex=regex)
        stream.write(s)
        return None

    @trace
    def show_collection(self, name, stream=sys.stderr):
        """Show the high-level commands executed by

            module show <collection>
        """
        collection = self.collections.get(name)
        if collection is None:
            logging.warning('{0!r} is not a collection'.format(name))
            return

        loaded = self.environ.get_loaded_modules('names', reverse=True)
        for m in loaded:
            stream.write("unload('{0}')\n".format(m))

        text = []
        for (directory, modules) in collection:
            text.append("use('{0}')".format(directory))
            for module in modules:
                m = create_module_from_kwds(**module)
                name = m.fullname
                opts = module['options']
                if opts:
                    s = "load('{0}', options={1!r})".format(name, opts)
                else:
                    s = "load('{0}')".format(name)
                text.append(s)
        pager('\n'.join(text)+'\n', plain=True)
        return 0
