#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/

set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

IMAGE_NAME="itisfoundation/service-integration:${OOIL_IMAGE_TAG:-master-github-latest}"
WORKDIR="$(pwd)"

run_with_color() {
  docker run \
    -it \
    --rm \
    --pull=newer \
    --volume="/etc/group:/etc/group:ro" \
    --volume="/etc/passwd:/etc/passwd:ro" \
    --user="$(id --user "$USER")":"$(id --group "$USER")" \
    --volume "$WORKDIR":/src \
    --workdir=/src \
    "$IMAGE_NAME" \
    "$@"
}

run() {
  docker run \
    --rm \
    --pull=newer \
    --volume="/etc/group:/etc/group:ro" \
    --volume="/etc/passwd:/etc/passwd:ro" \
    --user="$(id --user "$USER")":"$(id --group "$USER")" \
    --volume "$WORKDIR":/src \
    --workdir=/src \
    "$IMAGE_NAME" \
    "$@"
}

# ----------------------------------------------------------------------
# MAIN
#
# USAGE
#    ./scripts/ooil.bash --help

run "$@"
# ----------------------------------------------------------------------
