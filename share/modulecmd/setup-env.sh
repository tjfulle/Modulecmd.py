#!/bin/bash
# -*- shell-script -*-
if [[ ${-/x} != $- ]]; then
   echo "Start of pymod init/bash script to define the module command"
fi

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )"/.. >/dev/null && cd .. && pwd )"

PYMOD_DIR="${DIR}"
PYMOD_PKG_DIR="${PYMOD_DIR}"/lib/pymod/pymod
PYMOD_CMD="${PYMOD_DIR}"/bin/modulecmd.py
PYMOD_SESSION_ID=$$
MODULESHOME="${DIR}"
export PYMOD_PKG_DIR
export PYMOD_CMD
export PYMOD_DIR
export PYMOD_SESSION_ID
export MODULESHOME

########################################################################
#  Define the module command:  The first line runs the "pymod" command
#  to generate text:
#      export PATH="..."
#  then the "eval" converts the text into changes in the current shell.
module()
{
  eval $(python3 -E $PYMOD_CMD bash "$@")
}

PYMOD_VERSION="3.0.5"
export PYMOD_VERSION

export_module=$(echo "YES" | /usr/bin/tr '[:upper:]' '[:lower:]')
if [ -n "${BASH_VERSION:-}" -a "$export_module" != no ]; then
  export -f module
fi
unset export_module

########################################################################
#  Make tab completions available to bash users.

if [ ${BASH_VERSINFO:-0} -ge 3 ] && [ -r  "${PYMOD_DIR}"/share/pymod/bash_completions ] && [ -n "${PS1:-}" ]; then
 . "${PYMOD_DIR}"/share/pymod/bash_completions
fi

if [[ ${-/x} != $- ]]; then
   echo "End of pymod init/bash script to define the module command"
fi

# Local Variables:
# mode: shell-script
# indent-tabs-mode: nil
# End:
