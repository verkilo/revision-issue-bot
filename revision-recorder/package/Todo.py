
import uuid
import base64
import os
import yaml
from .TodoData import TodoData

class Todo:
  def __init__(self, contents, fname, file_contents=""):
    self.scope = 3
    self.fname = fname
    self.contents = contents
    self.has_changed = False
    self.has_new_key = False
    self.github = None
    self.stored = None
    self.file_contents = file_contents

    title, *body = contents.split("\n")
    body = " ".join(body)

    # Set Title and Key
    if title[0] == '-':
      key = title[1:13]
      title = title[14:]
    else:
      self.has_new_key = True
      s = str(uuid.uuid4())
      key = base64.urlsafe_b64encode(s.encode('utf-8'))
      title = title
      key = str(key, "utf-8")[:12]
 
    self.raw  = TodoData(key=key, title=title, body=body, location=fname)

    if self.has_new_key:
      self.update_key()

    # Get Stored Data
    if os.path.exists(self.raw.filename()):
      with open(self.raw.filename(), 'r') as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader) or {}
        self.stored = TodoData(**data)
        if not self.stored.key:
          self.stored.key = self.raw.key
    else:
      self.has_changed = True
      self.stored = self.raw

    self.context(file_contents)


  def check_changes(self):
    for key in ['body', 'location', 'title', 'context']:
      if self.raw.__dict__[key] != self.stored.__dict__[key]:
        self.has_changed = True
        self.stored.__dict__[key] = self.raw.__dict__[key]

    return self.has_changed


  def context(self, contents):
    if not self.raw.context:
      lines = contents.split("\n")
      scope = self.scope or 3
      for i, line in enumerate(lines):
        if self.contents in line:
          a = i - scope if (i - scope > 0) else 0
          b = i + scope if (i + scope < len(lines)) else len(lines) - 1
          x = lines[a:b]
          x.remove("")
          self.raw.context = "\n".join(x)
          break

    return self.raw.context

  def store(self):
    if self.check_changes():
      # Write to Github
      self.stored = self.github.store(self.stored)
      # Write to file system
      with open(self.stored.filename(), 'w') as yaml_file:
        yaml_file.write(str(self.stored))


  def update_key(self):
    x = "@tk {title}".format(title=self.raw.title)
    y = "@tk-{key} {title}".format(key=self.raw.key, title=self.raw.title)
    
    with open(self.raw.location, 'r') as mkd_file:
      contents = mkd_file.read().replace(x,y)

    # contents =contents
    with open(self.raw.location,'w') as f:
      f.write(contents)
      self.file_contents = contents
