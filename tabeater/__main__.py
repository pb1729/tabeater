from http.server import ThreadingHTTPServer
from http import HTTPStatus
from html import escape
from sched import scheduler

from db import Store
from init_db import ensure_db_exists
from tab_poller import launch_polling_thread
from event_server import create_event_server_class, ReplyStream, ErrStatus, EventQueue
from html_rendering import render_sessions


# constants
FILES_TO_SERVE = ['index.html', 'util.js', "style.css"]
FILES_TO_SERVE_BIN = ['favicon.svg', 'None']
PORT_NUM = 2693


class TabEater:
    def __init__(self):
        self._store = None
    @property # lazy initialization of db connection
    def store(self):
        if self._store is None:
            self._store = Store()
        return self._store
    def push(self, msg):
        EventQueue.send_event(
          (lambda rs: True), # send message to all reply streams
          msg)
    def rerender(self):
        sessions = self.store.load_sessions()
        tabs_html = render_sessions(sessions)
        self.push(tabs_html)
    def serve_file(self, fpath):
        if fpath in FILES_TO_SERVE:
            with open(fpath, 'r') as f:
                data = f.read()
                return data
        elif fpath in FILES_TO_SERVE_BIN:
            with open(fpath, 'rb') as f:
                data = f.read()
                return data
        else:
            return ErrStatus(404, "404: page not found")
    def GET(self, path, handler):
        if path[:8] == '/events/':
            return ReplyStream()
        elif path[:9] == '/refresh/':
            self.rerender()
            return "<xml></xml>"
        elif path == "/":
            return self.serve_file("index.html")
        elif path[:1] == '/':
            return self.serve_file(path[1:])
        else:
            return ErrStatus(404, "404: page not found")
    def POST(self, path, handler, post_body):
        if path[:10] == '/tab/lock/':
          tab_id = int(path[10:])
          lock = int(post_body)
          self.store.set_tab_lock(tab_id, lock)
          self.rerender()
          return "<xml></xml>"
    def DELETE(self, path, handler):
        if path[:9] == '/session/':
            sess_id = int(path[9:])
            self.store.delete_session(sess_id)
            self.rerender()
            return "<xml></xml>"
        elif path[:5] == '/tab/':
            tab_id = int(path[5:])
            self.store.delete_tab(tab_id)
            self.rerender()
            return "<xml></xml>"
        else:
            raise NotImplementedError("DELETE not implemented for this path!")


TabEaterEventServer = create_event_server_class("TabEaterEventServer",
  (lambda event_server: TabEater())) # create a new instance of TabEater every time...


def start_server():
    server_address = ('', PORT_NUM)
    print("Starting a server at: http://localhost:%d" % server_address[1])
    httpd = ThreadingHTTPServer(server_address, TabEaterEventServer)
    httpd.serve_forever()

def main():
    ensure_db_exists()
    launch_polling_thread()
    EventQueue.launch_worker()
    start_server()


if __name__ == "__main__":
    main()

