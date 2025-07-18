#!/bin/bash

for cid in $(docker ps -q); do
  cname=$(docker inspect --format '{{.Name}}' $cid | sed 's/^\\///')
  echo "============================"
  echo "Running diagnostics in $cname ($cid)"
  echo "============================"
  docker exec $cid /usr/local/bin/container_diagnostics.sh || echo "Failed to run diagnostics in $cname"
  echo
done