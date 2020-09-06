import github
import os

class Github:
  def __init__(self):
    self.label = os.getenv('REVISION_TAG', 'tk-revision')
    # ==================================================
    # Setup GH API
    token     = os.getenv('GITHUB_TOKEN', None)
    repo_name = os.getenv('GITHUB_REPOSITORY', None) \
      or os.environ( 'GITHUB_REPOSITORY', None)

    if repo_name and token:
      gh = github.Github(token)
      self.conn = gh.get_repo(repo_name)
    else:
      print("Repo not set, what's up?")


  def format(self, todo):
    """Common Body format for issues."""
    return """
## Body

{body}

## Context

```
{context}
```

[Read more](../blob/{branch}{location})
    """.format(
      branch=self.conn.default_branch,
      body=todo.body,
      context=todo.context,
      location=todo.location.replace('./', '/')
    )


  def resolve(self, todo):
    print("Resolving: #{} '{}'".format(todo.number, todo.title))
    i = self.conn.get_issue( todo.number )
    i.edit(state='closed')


  def store(self, todo):
    if todo.number:
      print("Updating: #{} '{}'".format(todo.number, todo.title))
      i = self.conn.get_issue( todo.number )
      i.edit(
        title=todo.title,
        body=self.format(todo)
      )
    else:
      res = self.conn.create_issue(
        title=todo.title,
        body=self.format(todo),
        labels=[self.label]
      )
      print("Adding: #{} '{}'".format(res.number, todo.title))
      todo.number = res.number
      todo.created_at = res.created_at

    return todo