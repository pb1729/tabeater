import os
import sqlite3


DB_FOLDER = "/persist"
DB_NAME = "/tabs.db"


class DBTab:
  def __init__(self, idx, sess, url, title, image):
    self.id = idx
    self.sess = sess
    self.url = url
    self.title = title
    self.image = image
  def save_to(self, cursor):
    cursor.execute("INSERT INTO tab(sess, url, title, image) VALUES (?, ?, ?, ?)",
      [self.sess, self.url, self.title, self.image])
  @staticmethod
  def from_parsed(tab, sess):
    """ initialize a DBTab from a regular Tab object derived by parsing """
    return DBTab(None, sess, tab.url, tab.title, tab.image)

class DBSession:
  def __init__(self, idx, name):
    self.id = idx
    self.name = name
  def save_to(self, cursor):
    cursor.execute("INSERT INTO sess(id, name) VALUES (?, ?)",
      [self.id, self.name])

class Store:
  db_path = os.getcwd() + DB_FOLDER + DB_NAME
  def __init__(self):
    self.db = sqlite3.connect(self.db_path)
  def save_session(self, sess_id, tabs):
    c = self.db.cursor()
    # ensure that this session exists
    DBSession(sess_id, "Session #%d" % sess_id).save_to(c)
    # make a list of any already-existing tabs belonging to this session
    c.execute("SELECT url FROM tab WHERE (sess=?)", [sess_id])
    prev = [tup[0] for tup in c.fetchall()]
    # save all current tabs
    curr = []
    for tab in tabs:
      DBTab.from_parsed(tab, sess_id).save_to(c)
      curr.append(tab.url)
    # remove tabs that existed previously but not now
    removed = set(prev) - set(curr)
    for url in removed:
      c.execute("DELETE FROM tab WHERE (sess=?) AND (url=?)", [sess_id, url])
    # finish up:
    self.db.commit()
  def load_tabs(self, sess_id):
    c = self.db.cursor()
    c.execute("SELECT * FROM tab WHERE (sess=?)", [sess_id])
    return [DBTab(*tup) for tup in c.fetchall()]
  def load_sessions(self):
    """ load all sessions and all tabs in those sessions """
    c = self.db.cursor()
    c.execute("SELECT * FROM sess")
    sessions = [DBSession(*tup) for tup in c.fetchall()]
    for session in sessions:
      # this is hacky, but we just tack an extra list of DBTab's onto the session for rendering
      session.tabs = self.load_tabs(session.id)
      session.tabs.sort(key=(lambda tab: tab.id)) # sort tabs by oldest first
    sessions.sort(key=(lambda sess: -sess.id)) # most recent sessions first
    return sessions
  def delete_tab(self, tab_id):
    c = self.db.cursor()
    c.execute("DELETE FROM tab WHERE (id=?)", [tab_id])
    self.db.commit()
  def delete_session(self, sess_id):
    c = self.db.cursor()
    c.execute("DELETE FROM sess WHERE (id=?)", [sess_id])
    c.execute("DELETE FROM tab WHERE (sess=?)", [sess_id])
    self.db.commit()



