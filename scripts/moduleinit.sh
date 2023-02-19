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
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && cd .. && pwd )"

PYMOD_DIR="${DIR}"
PYMOD_PKG_DIR="${PYMOD_DIR}"/modulecmd
PYMOD_CMD="${PYMOD_DIR}"/scripts/modulecmd.py
PYMOD_SESSION_ID=$$
MODULESHOME="${DIR}"
export PYMOD_PKG_DIR
export PYMOD_CMD
export PYMOD_DIR
export PYMOD_SESSION_ID
export MODULESHOME
export PYTHONPATH=${PYMOD_DIR}

########################################################################
mc()
{
  python3 -E -m modulecmd "$@"
}
