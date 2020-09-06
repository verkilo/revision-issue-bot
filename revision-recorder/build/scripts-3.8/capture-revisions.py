#!python

from package.Todos import Todos

if __name__ == "__main__":
  todos = Todos()
  for t in todos.get_all():
    t.store()

  files = todos.prune()