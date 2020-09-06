import yaml

class TodoData:
  """Holds the relevant Todo Data"""
  def __init__(self, **kwargs):
    self.key = None
    self.title = ""
    self.body = ""
    self.context = ""
    self.location = None
    self.number = None
    self.created_at = None
    for k, v in kwargs.items():
      if isinstance(v, str):
        if k == 'body':
          v = v.replace('@body','')
        v = v.strip()
      setattr(self, k, v)

  def filename(self):
    if self.key is None:
      print("KEY:",self.key)
      raise FileError("Key is null, so cannot access file")
    return ".verkilo/.revision-data/" + self.key + ".yml"

  def __str__(self):
    return yaml.dump(self.__dict__, default_flow_style=False)