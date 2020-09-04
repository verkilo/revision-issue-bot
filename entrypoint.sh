#!/bin/bash

# Ensure that the GITHUB_TOKEN secret is included
if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "Set the GITHUB_TOKEN env variable."
  exit 1
fi
# owner=$GITHUB_REPOSITORY_OWNER
# reponame=$(basename $GITHUB_REPOSITORY)
# echo $GITHUB_REPOSITORY
# echo "todo.py --repo ${owner}/${reponame}} --credentials ${GITHUB_TOKEN}"
todo.py
exit 0
