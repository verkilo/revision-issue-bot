#!/usr/bin/env python

import argparse
from github import Github
import pprint
import glob
import re
import hashlib
import yaml

def get_files(dir="./"):
  """Read all files in the target director"""
  files = []
  for filename in glob.iglob(dir + '**/*.md', recursive=True):
     files.append(filename)

  return files

def create_issue(repo, issue, label):
  """Create a new issue."""
  if repo:
    # print("   .. Created ({title})", title=issue['title'])
    body = """
Body: {body}

[Read more at {file}](../blob/{branch}{file})
    """.format(
      branch=repo.default_branch,
      body=issue['body'],
      file=issue['location'].replace('./','/')
    )
    res = repo.create_issue(
      title=issue['title'],
      body=body,
      labels=[label]
    )
    # res.create_comment("Opened by Revision bot.")
    issue['number'] = res.number
    issue['created_at'] = res.created_at
  else:
    print("   .. Skipped because no repository identified.")

  return issue


def resolve_issue(repo, issue):
  """Resolve an issue no longer found in the text"""
  gh_issue = repo.get_issue(
    issue['number']
  )
  gh_issue.edit(state='closed')
  # print("   .. Resolved ({title})", title=issue['title'])


def parse_actions(actions,file):
  with open(file, 'r') as mkd_file:
    contents = mkd_file.read()

  todos = re.findall('<!-- @tk (.*?)-->',contents,re.MULTILINE|re.DOTALL)

  if todos:
    for action in todos:
      title = ""
      body  = ""
      has_body = re.findall('@body', action, re.MULTILINE|re.DOTALL)
      if has_body:
        title, body = action.split('@body')
        title = title.strip()
      else:
        title = action.split("\n")[0].strip()

      key = hashlib.md5(title.encode('utf-8')).hexdigest()
      actions[key] = {
        "title": title,
        "body" : body,
        "location": file
      }

  return actions


def cleanse(s):
  s = s.replace('//','/')
  s = s.replace('../','')
  return s


def get_revision_guide(guide_file):
  guide = {}
  try:
    with open(guide_file) as file:
      # The FullLoader parameter handles the conversion from YAML
      # scalar values to Python the dictionary format
      guide = yaml.load(file, Loader=yaml.FullLoader)
  except IOError:
    print('No revision guide to read, returning empty list')

  return guide


def main():
  # Read/parse arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("--credentials", dest='credentials', help="GH API Credentials")
  parser.add_argument("--guide",   dest='guide',  help="guide file")
  parser.add_argument("--quiet",   help="Don't print progress", action="store_true")
  parser.add_argument("--repo",   dest='repo_name',  help="Don't print progress")
  parser.add_argument("--target", dest='target', help="target directory")
  parser.add_argument("--label", dest='label', help="issue label")
  parser.add_argument("--test",  help="Show, don't do anything", action="store_true")
  parser.parse_known_args()
  args = parser.parse_args()

  guide_file = "./.github/revision-guide.yml"
  if args.guide:
    guide_file = cleanse("./{guide}".format(guide.args.guide))

  target_dir = "./src/"
  if args.target:
    target_dir = cleanse("./{target}/".format(target=args.target))

  label='tk-revision'
  if args.label
    label=args.label.strip()

  # Setup GH API
  repo = None
  branch = ""
  if args.repo_name and args.credentials:
    repo_name = args.repo_name
    github = Github(args.credentials)
    repo = github.get_repo(repo_name)
  else:
    print("No repo, so no changes happening.")

  # ==================================================
  # Initialize / Read current state
  actions = {}
  guide = get_revision_guide(guide_file)

  # Get the current issues from source files.
  for fname in get_files(target_dir):
    parse_actions(actions, fname)

  # ==================================================
  # With a properly created repository, we will create or resolve.
  if repo:
    # Create Issues
    print("Creating:")
    new_issues = [k for k in actions if k not in guide]
    for key in new_issues:
      issue = actions[key]
      if args.test:
        print(".. {key} ({title})".format(key=key,title=issue['title']))
      else:
        actions[key] = create_issue(repo, issue, label)

    # Resolve Issues
    print("Resolving:")
    resolved_issues = [k for k in guide if k not in actions]
    for key in resolved_issues:
      issue = guide[key]
      if args.test:
        print(".. {key} ({title})".format(key=key,title=issue['title']))
      else:
        resolve_issue(repo, guide[key])

    # Store active issues in Revision Guide.
    with open(guide_file, 'w') as yaml_file:
      yaml.dump(actions, yaml_file, default_flow_style=False)


if __name__ == "__main__":
  main()
