import os
import sqlite3

from db import DB_FOLDER, DB_NAME


def ensure_dir_exists():
  newdirpath = os.getcwd() + DB_FOLDER
  if not os.path.exists(newdirpath):
    os.makedirs(newdirpath)
    print("Created a new directory %s" % newdirpath)

def ensure_file_exists():
  dbpath = os.getcwd() + DB_FOLDER + DB_NAME
  if not os.path.exists(dbpath):
    with open('schema.sql', 'r') as f:
      schema_script = f.read()
    db = sqlite3.connect(dbpath)
    c = db.cursor()
    c.executescript(schema_script)
    print("Initialized a new DB at %s" % dbpath)


def ensure_db_exists():
  ensure_dir_exists()
  ensure_file_exists()


if __name__ == '__main__':
  ensure_db_exists()


