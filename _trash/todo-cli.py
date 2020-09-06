#!/usr/local/bin/python3

import argparse
from github import Github
import pprint
import glob
import re
import hashlib
import uuid
import base64
import os
import yaml

debug = False

class Action:
  def __init__(self, location, contents, raw):
    self.raw      = raw
    self.contents = ""
    self.location = location

def get_files(dir="./"):
  """Read all files in the target director"""
  files = []
  for filename in glob.iglob(dir + '**/*.md', recursive=True):
     files.append(filename)

  return files


def create_issue(repo, issue, label, key):
  """Create a new issue."""
  global debug
  print("..",issue['title'])
  if repo and not debug:
    # print("   .. Created ({title})", title=issue['title'])
    body = issue_body(
      issue['body'], repo.default_branch, issue['location'], issue['context']
    )
    res = repo.create_issue(
      title=issue['title'],
      body=body,
      labels=[label]
    )
    issue['number'] = res.number
    issue['created_at'] = res.created_at
  else:
    print("   .. Skipped because no repository identified.")

  tweak_todo(key, issue['title'], issue['location'])

  issue.pop('context', 'No Key found')
  return issue


def update_issue(repo, guide, action, key):
  """Update a portion of the issue based on the changed value."""
  global debug
  gh_issue = repo.get_issue( guide['number'] )
  is_updated = False

  if action['body'] != guide['body']:
    print(".. (body)", action['title'])
    body = issue_body(
      action['body'], repo.default_branch, action['location'], action['context']
    )
    guide['body'] = action['body']
    if repo and not debug:
      gh_issue.edit(body=body)
      gh_issue.create_comment(
        "Updated body to '{body}'".format(body=action['body'])
      )
      is_updated = True

  if action['title'] != guide['title']:
    print(".. (title)", action['title'])
    guide['title'] = action['title']
    if repo and not debug:
      gh_issue.edit(title=action['title'])
      is_updated = True
  
  if is_updated:
    tweak_todo(key, action['title'], action['location'])

  guide.pop('context', 'No Key found')
  return guide


def resolve_issue(repo, issue):
  """Resolve an issue no longer found in the text"""
  print("..",issue['title'])
  gh_issue = repo.get_issue(
    issue['number']
  )
  if repo and not debug:
    gh_issue.edit(state='closed')


def gen_key():
  """Create a shortened key"""
  s = str(uuid.uuid4())
  key = base64.urlsafe_b64encode(s.encode('utf-8'))
  return str(key, "utf-8")[:12]


def get_context(key, contents):
  lines = contents.split("\n")
  context = ""
  scope = 5
  for i, line in enumerate(lines):
    if key in line:
      a = i - scope
      a = 0 if (a < 0) else a
      b = i + scope
      b = len(lines) - i if (b > len(lines)) else b
      context = "\n".join(lines[a:b])
      break

  return context


def tweak_todo(key, title, file):
  x = "@tk {title}".format(title=title)
  y = "@tk-{key} {title}".format(key=key, title=title)
  
  with open(file, 'r') as mkd_file:
    contents = mkd_file.read().replace(x,y)

  # contents =contents
  with open(file,'w') as f:
    f.write(contents)    


def parse_actions(actions,location):
  with open(location, 'r') as mkd_file:
    contents = mkd_file.read()

  todos = re.findall('<!-- @tk(.*?)-->',contents,re.MULTILINE|re.DOTALL)
  if todos:
    for action in todos:

      # akshun = Action(location, contents, action)
      title = ""
      body  = ""
      has_body = re.findall('@body', action, re.MULTILINE|re.DOTALL)
      
      if has_body:
        title, body = action.split('@body')
        title = title.strip()
        body = body.strip()

      else:
        title = action.split("\n")[0].strip()

      # Do I have a key? If so, use it. Otherwise make it.
      if title[0] == '-':
        key = title[1:13]
        title = title[14:]
      else:
        key = gen_key()

      actions[key] = {
        "title": title,
        "body" : body,
        "context" : get_context(title, contents),
        "location": location
      }

  return actions


def cleanse(s):
  s = s.replace('//','/')
  s = s.replace('../','')
  return s


def issue_body(body, branch, location, context):
  return """
## Body

{body}

## Context

```
{context}
```

[Read more](../blob/{branch}{location})
    """.format(
      branch=branch,
      body=body,
      context=context,
      location=location.replace('./', '/')
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
  global debug

  # ==================================================
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

  # ==================================================
  # Setup GH API
  token     = os.getenv('GITHUB_TOKEN', None)
  repo_name = os.getenv('GITHUB_REPOSITORY', None) or os.environ(
      'GITHUB_REPOSITORY', None)
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
            guide[key] = create_issue(repo, issue, label, key)

    # Resolve Issues
    resolved_issues = [k for k in guide if k not in actions]
    if resolved_issues:
        print("Resolving:")
        for key in resolved_issues:
          issue = guide.pop(key)
          if args.test:
            print(".. {key} ({title})".format(key=key,title=issue['title']))
          else:
            resolve_issue(repo, issue)

    # Update Issues?
    issues = [k for k in actions if k in guide]
    if issues: 
      print("Checking for updates:")
      for key in issues:
        a = actions[key]
        g = guide[key]
        guide[key] = update_issue(repo, g, a, key)

    # Store active issues in Revision Guide.
    if not debug:
      with open(guide_file, 'w') as yaml_file:
        yaml.dump(guide, yaml_file, default_flow_style=False)


if __name__ == "__main__":
  main()
