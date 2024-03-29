import lz4.block
import json
import base64


class Tab:
  def __init__(self, tab_dict):
    most_recent = tab_dict["entries"][tab_dict["index"] - 1]
    self.url = most_recent["url"]
    self.title = most_recent["title"] if "title" in most_recent else "---"
    self.image = tab_dict["image"] if "image" in tab_dict else None


def lz4read(path):
  """ from here: https://gist.github.com/Tblue/62ff47bef7f894e92ed5 """
  with open(path, "rb") as f:
    if f.read(8) != b"mozLz40\0":
      raise ValueError("Invalid magic number!")
    return lz4.block.decompress(f.read())

def lzjson_read(path):
  return json.loads(lz4read(path))

def get_tabs(session_dict):
  """ get all tabs for a session as a list of windows, each window being a list of tabs """
  ans = []
  for window in session_dict["windows"]:
    tabs = []
    for tab_dict in window["tabs"]:
      tabs.append(Tab(tab_dict))
    ans.append(tabs)
  return ans

def get_session_id(session_dict):
  """ session id is the timestamp of the session's start time """
  return session_dict["session"]["startTime"]



