import os


FF_FOLDER_LOCATIONS = ["/.mozilla/firefox/", "/snap/firefox/common/.mozilla/firefox/"]
PROFILES_FNAME = "profiles.ini"
SESSIONS_LOC = "/sessionstore-backups/recovery.jsonlz4"


def get_home():
  if not hasattr(get_home, "ans"):
    get_home.ans = os.environ["HOME"]
  return get_home.ans


def get_ff_profile():
  """ gets the firefox profile folder location.
  prompts user to select a profile if there is more than one. """
  paths_list = []
  for ff_folder_loc in FF_FOLDER_LOCATIONS:
    base_path = get_home() + ff_folder_loc
    try:
      with open(base_path + PROFILES_FNAME, "r") as f_profiles:
        for line in f_profiles.readlines():
          if line[:5] == "Path=":
            paths_list.append(base_path + line[5:-1])
    except FileNotFoundError: continue
  if len(paths_list) == 0:
    return None
  if len(paths_list) > 1:
    for i, path in enumerate(paths_list):
      print(i, path)
    idx = None
    while idx is None:
      try:
        idx = int(input("Multiple profiles found, enter the index of the one to use? > "))
        assert 0 <= idx < len(paths_list)
      except (ValueError, AssertionError):
        print("Should enter a valid integer from the options above!")
  else:
    idx = 0
  return paths_list[idx]


def get_ff_session_file():
  return get_ff_profile() + SESSIONS_LOC


if __name__ == "__main__":
  print(get_ff_profile())


