==================
The module Command
==================

The ``Modulecmd.py`` initialization defines the ``module`` shell function that executes ``Modulecmd.py`` modules.  Valid subcommands of ``module`` are:

.. code-block:: console

   modify environment:
     load (add)            Load modules into environment
     unload (rm)           Unload modules from environment
     reload                Reload a loaded module
     swap                  Swaps two modules, effectively unloading the first then loading the second
     purge                 Remove all loaded modules
     refresh               Unload and reload all loaded modules
     avail (av)            Displays available modules
     info                  Provides information on a particular loaded module
     reset                 Reset environment to initial state

   clones:
     clone                 Manipulate cloned environments

   collections:
     save                  Save loaded modules
     restore               Restore saved modules or, optionally, a clone
     remove                Remove saved collection of modules

   informational:
     list (ls)             Display loaded modules
     whatis                Display module whatis string.  The whatis string is a short informational
                           message a module can provide.  If not defined by the module, a default is
                           displayed.
     show                  Show the commands that would be issued by module load
     cat                   Print contents of a module or collection to the console output.
     more                  Print contents of a module or collection to the console output one
                           page at a time.  Allows movement through files similar to shell's `less`
                           program.
     find (which)          Show path to module file

   modulepath:
     path                  Show MODULEPATH
     use                   Add (use) directory[s] to MODULEPATH
     unuse                 Remove (unuse) directory[s] from MODULEPATH
