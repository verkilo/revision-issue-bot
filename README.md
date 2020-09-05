# Revision Guide Bot

<!-- revision-guide-bot-readme -->
**Revision Guide Bot** is a Docker container that auto-generates Github Issues from TODO annotations in the source material.
<!-- /revision-guide-bot-readme -->

## Configuration

The following Github Action workflow should be added. Your repository name needs to be added

```
name: Revision Issues Maintainer (on Demand)
on: [push]
jobs:
  build:
    if: "!contains(toJSON(github.event.commits.*.message), '@verkilo logged revision issues')"
    name: Log revision issues
    runs-on: ubuntu-latest
    steps:
      - name: Get repo
        uses: actions/checkout@main
        with:
          ref: main
      - name: Run bot (Docker)
        uses: docker://merovex/revision-issue-bot:latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit on change
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "@verkilo logged revision issues"
```