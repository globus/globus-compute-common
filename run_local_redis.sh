#!/bin/bash
set -euo pipefail

echo '
Spinning up a local redis instance in docker for testing purposes!

This is not the same as the redis that may be deployed with helm, k8s, etc.

You can shut down and remove the container with

    docker kill globus-compute-common-test-redis
    docker rm globus-compute-common-test-redis


'

echo "turning on '-x' ..."
set -x

docker run -d -p 6379:6379 --name globus-compute-common-test-redis redis
