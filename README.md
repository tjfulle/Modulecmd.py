[![codecov](https://codecov.io/gh/tjfulle/Modulecmd.py/branch/master/graph/badge.svg)](https://codecov.io/gh/tjfulle/Modulecmd.py/branch/master)
[![Build Status](https://travis-ci.org/tjfulle/Modulecmd.py.svg?branch=master)](https://travis-ci.org/tjfulle/Modulecmd.py)

# Introduction

`Modulecmd.py` is an environment module system inspired by TCL [Environment Modules](http://modules.sourceforge.net) and Lua [lmod](https://lmod.readthedocs.io/en/latest/) and written in Python.  `Modulecmd.py` is compatible with Python 2.6, 2.7, and 3.5+.  `Modulecmd.py` does not require any additional compilation.

`Modulecmd.py` provides a framework for processing module files written in Python.  Additionally, `Modulecmd.py` processes TCL modules by wrapping the TCL module command.  TCL compatibility requires that `tclsh` be found on the user's `PATH` (the TCL module command is provided by `Modulecmd.py`).  Likewise, `lmod` can process most TCL modules.


# Installation

Clone or download `Modulecmd.py`.  In your `.bashrc`, execute the following:

```sh
source ${MODULECMD_PY_DIR}/share/pymod/setup-env.sh
module init -p=${MODULEPATH}
```

where `${MODULECMD_PY_DIR}` is the path to the directory where `Modulecmd.py`
is cloned. The second command above (`module init-p=${MODULEPATH}`) instructs
`Modulecmd.py` to do some initialization tasks and is not strictly necessary.
