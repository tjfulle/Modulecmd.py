#!/bin/bash -e

QA_DIR="$(dirname ${BASH_SOURCE[0]})"
export PYMOD_ROOT=$(realpath "$QA_DIR/../../..")

# Source the setup script
. "$PYMOD_ROOT/share/pymod/setup-env.sh"

# Move to root directory of pymod
# Allows script to be run from anywhere
cd "$PYMOD_ROOT"

# Run unit tests with code coverage
extra_args=""
if [[ -n "$@" ]]; then
    extra_args="-k $@"
fi
coverage run bin/pymod bash test --verbose "$extra_args"
