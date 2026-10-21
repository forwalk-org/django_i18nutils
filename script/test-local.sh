#!/bin/bash

# """
# Tox-in-Docker Test Runner
#
# This script executes 'tox' inside the 'painless/tox' container.
#
# """

IMAGE="divio/multi-python"
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "--- Starting Tox inside $IMAGE ---"

# -v "$(pwd)":/src: Mounts your code to a neutral directory
# -w /src: Sets the working directory
# -e HOME=/tmp: Provides a writable home for Python/Tox cache
docker run --rm \
  --entrypoint "" \
  -v "$(pwd)":/src \
  -w /src \
  -u "${USER_ID}:${GROUP_ID}" \
  -e HOME=/tmp \
  "$IMAGE" tox "$@"

echo "--- Testing complete ---"
