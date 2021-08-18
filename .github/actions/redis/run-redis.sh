#!/bin/bash
set -euxo pipefail

IMAGE="redis:$REDIS_VERSION"

docker network create redisnet

docker run \
  --rm \
  --publish "6379:6379" \
  --detach \
  --network=redisnet \
  --name="redis" \
  "$IMAGE"

echo "redis up and running"
