#!/bin/bash

# Ensure that the GITHUB_TOKEN secret is included
if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "Set the GITHUB_TOKEN env variable."
  exit 1
fi
reponame=$(basename $GITHUB_REPOSITORY)
args = "--repo ${reponame}"

if [["$GUIDE_FILE"]]
  args = "${args} --guide ${GUIDE_FILE}"
fi
if [["$TARGET_DIR"]]
  args = "${args} --target ${TARGET_DIR}"
fi

todo.py ${args}
exit 0
