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

MODULECMD_DIR="${DIR}"
MODULECMD_PKG_DIR="${MODULECMD_DIR}"/modulecmd
MODULECMD_SESSION_ID=$$
MODULESHOME="${DIR}"
export MODULECMD_PKG_DIR
export MODULECMD_CMD
export MODULECMD_DIR
export MODULECMD_SESSION_ID
export MODULESHOME
export PYTHONPATH=${MODULECMD_DIR}

########################################################################
mc()
{
  PYTHONPATH=${MODULECMD_DIR} python3 -E -m modulecmd "$@"
}
