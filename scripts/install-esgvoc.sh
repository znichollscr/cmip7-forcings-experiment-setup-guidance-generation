#!/bin/bash
# Handy trick (full details here https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425?permalink_comment_id=3799230):
# -e: exit immediately if any command fails
# -u: exit if you reference any unset variable
# -o: pipefail means that a non-zero exit code is returned if any command in the script fails
set -euo pipefail

# Create the CMOR CVs JSON file
#
# `uv run bash install-esgvoc.sh`
#
# Works in the currently activated environment,
# therefore we recommend creating and activating a virtual environment
# before running this script (we use Python 3.13 in our CI at the time of writing).
#
# Options:
#
# -v: verbose mode
#
# If you're on windows, sorry.
# You should be able to more or less copy these commands out.

# Environment variables that this file uses.
# If they're not set, the default values are used.
### Non-versioned esgvoc config
# Use when we are using a branches of CVs
# esgvoc_versioned=0
# # UNIVERSE_CVS_FORK="${UNIVERSE_CVS_FORK:=znichollscr}"
# # UNIVERSE_CVS_REF="${UNIVERSE_CVS_REF:=add-dcpp-entries}"
# UNIVERSE_CVS_FORK="${UNIVERSE_CVS_FORK:=WCRP-CMIP}"
# UNIVERSE_CVS_REF="${UNIVERSE_CVS_REF:=esgvoc_dev}"
# CMIP7_CVS_FORK="${CMIP7_CVS_FORK:=WCRP-CMIP}"
# CMIP7_CVS_REF="${CMIP7_CVS_REF:=esgvoc_dev}"
# # CMIP7_CVS_REF="${CMIP7_CVS_REF:=latest-fixes}"

### Versioned esgvoc config
# Use when we are using a versioned esgvoc release
esgvoc_versioned=1
ESGVOC_CMIP7_DB_VERSION="${ESGVOC_CMIP7_DB_VERSION:=latest}"

verbose=0

while getopts "r:v" OPTION; do
    case $OPTION in
    v) verbose=1 ;;
    *)
        echo "usage: $0 [-v]" >&2
        exit 1
        ;;
    esac
done

function log() {
    if [[ $verbose -eq 1 ]]; then
        echo "$@"
    fi
}

if [[ $esgvoc_versioned -eq 1 ]]; then

    echo "Using versioned esgvoc"
    log "ESGVOC_CMIP7_DB_VERSION=$ESGVOC_CMIP7_DB_VERSION"
    esgvoc use "cmip7@${ESGVOC_CMIP7_DB_VERSION}"

else

    echo "Using non-versioned esgvoc"
    log "UNIVERSE_CVS_FORK=$UNIVERSE_CVS_FORK"
    log "UNIVERSE_CVS_REF=$UNIVERSE_CVS_REF"
    log "CMIP7_CVS_FORK=$CMIP7_CVS_FORK"
    log "CMIP7_CVS_REF=$CMIP7_CVS_REF"

    esgvoc admin build \
        --project-repo "https://github.com/${CMIP7_CVS_FORK}/CMIP7-CVs" \
        --project-ref "${CMIP7_CVS_REF}" \
        --universe-repo "https://github.com/${UNIVERSE_CVS_FORK}/WCRP-universe" \
        --universe-ref "${UNIVERSE_CVS_REF}" \
        --project-id cmip7 \
        --cv-version dev \
        --universe-version dev \
        --output /tmp/cmip7.db

    esgvoc admin install cmip7 /tmp/cmip7.db --name local --activate

fi
