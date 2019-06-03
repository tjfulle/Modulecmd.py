Installation
============

Clone or download ``Modulecmd.py`` and source the appropriate setup script in your shell's initialization script. The ``Modulecmd.py`` initialization defines the ``module`` shell function that executes ``Modulecmd.py`` modules.

----
Bash
----

In your ``.bashrc``, add the following:

.. code-block:: shell

  source ${MODULECMD_PY_DIR}/share/pymod/setup-env.sh
  module init -p=${MODULEPATH}

where ``${MODULECMD_PY_DIR}`` is the path to the directory where ``Modulecmd.py`` is cloned.

