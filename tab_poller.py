import time
import threading

from get_ff_profile import get_ff_session_file
from lz4parse import lzjson_read, get_tabs, get_session_id
from db import Store

PERIOD = 3 # polling period [s]


def get_current_tabs():
  """ returns the start time of the session and all tabs in the session """
  jsondata = lzjson_read(get_ff_session_file())
  sess_id = get_session_id(jsondata)
  windows = get_tabs(jsondata)
  all_tabs = []
  for window in windows:
    for tab in window:
      all_tabs.append(tab)
  return sess_id, all_tabs

def record_current_session(store):
  try:
    sess_id, tabs = get_current_tabs()
    store.save_session(sess_id, tabs)
  except FileNotFoundError as e:
    print(e)

def do_polling():
  store = Store() # get a db connection
  while True:
    try:
      record_current_session(store)
    except FileNotFoundError:
      pass # not a big problem if file is not present when the browser is closed
    except BaseException as e:
      print(e)
    time.sleep(PERIOD)

def launch_polling_thread():
  """ launch a separate thread to poll the session file and save the data to the db """
  t = threading.Thread(target=do_polling)
  t.start()






