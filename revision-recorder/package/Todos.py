from .Github import Github
import glob 
import os
import re
import yaml
from pathlib import Path
from .TodoData import TodoData
from .Todo import Todo

class Todos:
  def __init__(self):
    self.todos = []
    self.files = []
    self.keys  = []
    self.github = Github()
    os.makedirs('.verkilo/.revision-data', exist_ok = True)
    Path('.verkilo/.revision-data/.keep', exist_ok = True).touch()

  def prune(self):
    keys  = []
    files = {}
    for fname in glob.iglob('.verkilo/.revision-data/**/*yml', recursive=True):
      k = os.path.basename(fname).replace('.yml','')
      files[k] = fname

    for t in self.todos:
      keys.append(t.raw.key)
    
    delta = [k for k in files if k not in keys]

    if delta:
      for k in delta:
        with open(files[k]) as file:
          data = yaml.load(file, Loader=yaml.FullLoader) or {}
          data = TodoData(**data)
          self.github.resolve(data)
          os.remove(data.filename())


  def get_all(self):
    """Read in all TODOs in files"""
    pat = re.compile('(<!-- @tk(.*?)-->)',re.M|re.S|re.I)
    for dir in glob.iglob('./**/.book', recursive=True):
      for fname in glob.iglob(os.path.dirname(dir) + '/**/*md', recursive=True):
          with open(fname, 'r') as mkd_file:
            contents = mkd_file.read()

            for todo in re.findall(pat,contents):
              t = Todo(todo[1],fname)
              t.context(contents)
              t.github = self.github
              self.todos.append(t)

          self.files.append(fname)
    
    return self.todos

