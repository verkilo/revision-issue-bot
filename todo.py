#!/usr/local/bin/python3

import argparse
from github import Github
import pprint
import glob
import re
import hashlib
import os
import yaml

def get_files(dir="./"):
  """Read all files in the target director"""
  files = []
  for filename in glob.iglob(dir + '**/*.md', recursive=True):
     files.append(filename)

  return files


def create_issue(repo, issue, label):
  """Create a new issue."""
  print("..",issue['title'])
  if repo:
    # print("   .. Created ({title})", title=issue['title'])
    body = issue_body(issue['body'], repo.default_branch, issue['location'])
    res = repo.create_issue(
      title=issue['title'],
      body=body,
      labels=[label]
    )
    issue['number'] = res.number
    issue['created_at'] = res.created_at
  else:
    print("   .. Skipped because no repository identified.")

  return issue


def update_issue(repo, guide, action, key):
  """Update a portion of the issue based on the changed value."""
  gh_issue = repo.get_issue( guide['number'] )

  if action['body'] != guide['body']:
    print(".. (body)", action['title'])
    body = issue_body(action['body'], repo.default_branch, action['location'])
    guide['body'] = action['body']
    gh_issue.edit(body=body)
    gh_issue.create_comment(
      "Updating body to '{body}'".format(body=action['body'])
    )

  if action['title'] != guide['title']:
    print(".. (title)", action['title'])
    guide['title'] = action['title']
    gh_issue.edit(title=action['title'])
    gh_issue.create_comment(a
        "Updating title to '{title}'".format(title=action['title'])
    )
  
  return guide


def resolve_issue(repo, issue):
  """Resolve an issue no longer found in the text"""
  print("..",action['title'])
  gh_issue = repo.get_issue(
    action['number']
  )
  gh_issue.edit(state='closed')


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
        body = body.strip()

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


def issue_body(body, branch, location):
  return """
Body: {body}

[Read more at {file}](../blob/{branch}{file})
    """.format(
      branch=branch,
      body=body,
      file=location.replace('./', '/')
  )


def get_revision_guide(guide_file):
  guide = {}
  try:
    with open(guide_file) as file:
      # The FullLoader parameter handles the conversion from YAML
      # scalar values to Python the dictionary format
      guide = yaml.load(file, Loader=yaml.FullLoader) or {}

  except IOError:
    print('No revision guide to read, returning empty list')
    return {}

  return guide


def main():
  # Read/parse arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("--guide",   dest='guide',  help="guide file")
  parser.add_argument("--target", dest='target', help="target directory")
  parser.add_argument("--label", dest='label', help="issue label")
  parser.add_argument("--test",  help="Show, don't do anything", action="store_true")
  parser.parse_known_args()
  args = parser.parse_args()

  guide_file = "./.verkilo/revision-guide.yml"
  if args.guide:
    guide_file = cleanse("./{guide}".format(guide.args.guide))

  target_dir = "./src/"
  if args.target:
    target_dir = cleanse("./{target}/".format(target=args.target))

  label='tk-revision'
  if args.label:
    label=args.label.strip()

  token     = os.getenv('GITHUB_TOKEN', None)
  repo_name = os.getenv('GITHUB_REPOSITORY', None) or os.environ(
      'GITHUB_REPOSITORY', None)

  # Setup GH API
  repo = None
  if repo_name and token:
    github = Github(token)
    repo = github.get_repo(repo_name)
  else:
    print("Repo not set, what's up?")

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
    new_issues = [k for k in actions if k not in guide]
    if new_issues:
        print("Creating:")
        for key in new_issues:
          issue = actions[key]
          if args.test:
            print(".. {key} ({title})".format(key=key,title=issue['title']))
          else:
            guide[key] = create_issue(repo, issue, label)

    # Resolve Issues
    resolved_issues = [k for k in guide if k not in actions]
    if resolved_issues:
        print("Resolving:")
        for key in resolved_issues:
          issue = guide[key]
          if args.test:
            print(".. {key} ({title})".format(key=key,title=issue['title']))
          else:
            pass 
            #resolve_issue(repo, issue)
            #del guide[key]

    # Update Issues?
    issues = [k for k in actions if k in guide]
    if issues: 
      print("Checking for updates:")
      for key in issues:
        a = actions[key]
        g = guide[key]
        guide[key] = update_issue(repo, g, a, key)

    # Store active issues in Revision Guide.
    with open(guide_file, 'w') as yaml_file:
      yaml.dump(guide, yaml_file, default_flow_style=False)


if __name__ == "__main__":
  main()
