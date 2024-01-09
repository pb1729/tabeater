from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from html import escape
from queue import Queue
import threading


class ErrStatus:
  def __init__(self, status, msg=""):
    self.status = status
    self.msg = msg

class ReplyStream:
  def __init__(self):
    self.handler = None
  def push(self, text):
    cleaned = text.replace("\n", "") # newlines are separators and should be removed
    if self.handler != None:
      try:
        self.handler.send_text('data: %s\n\n' % cleaned)
      except OSError: # socket has been closed
        EventQueue.del_reply_stream(self)

class EventServer(BaseHTTPRequestHandler):
  """ overrides the do_GET, do_POST, do_DELETE methods to allow sending of events
    this is an abstract base class in that it does not define the "get responder" method. """
  def send_reply(self, reply):
    if isinstance(reply, ErrStatus):
      self.reply_with_error_status(reply)
    elif isinstance(reply, ReplyStream):
      self.reply_with_stream(reply)
    else:
      self.reply_with_text(reply)
  def reply_with_error_status(self, err_status):
    self.send_response(err_status.status)
    self.end_headers()
    self.send_text(err_status.msg)
  def reply_with_text(self, text):
    self.send_response(HTTPStatus.OK)
    self.end_headers()
    self.send_text(text)
  def reply_with_stream(self, reply_stream):
    self.close_connection = False
    self.send_response(HTTPStatus.OK)
    self.send_header('Content-Type', 'text/event-stream')
    self.end_headers()
    reply_stream.handler = self # tell the stream how to send data back to the client
    EventQueue.add_reply_stream(reply_stream) # allow the stream to listen to events
  def send_text(self, text):
    if isinstance(text, bytes):
      pass
    elif isinstance(text, str):
      text = bytes(text, 'utf-8')
    else:
      raise ValueError("Expected to be passed a bytestring or string!")
    self.wfile.write(text)
    self.wfile.flush()
  def do_GET(self):
    responder = self.get_responder()
    self.send_reply(responder.GET(self.path, self))
  def do_POST(self):
    responder = self.get_responder()
    self.send_reply(responder.POST(self.path, self))
  def do_DELETE(self):
    responder = self.get_responder()
    self.send_reply(responder.DELETE(self.path, self))


class EventQueue:
  """ a static class that maintains a thread-safe queue for sending events to ReplyStreams """
  reply_streams = []
  queue = Queue()
  @classmethod
  def send_event(cls, is_target, msg):
    """ send a message msg to the target ReplyStreams.
      is_target is a function that returns True when passed a reply stream that should
      recieve the message. You can tack "hair" onto streams to give your is_target
      function something to distinguish. """
    cls.queue.put(("SEND", is_target, msg, None))
  @classmethod
  def add_reply_stream(cls, rs):
    """ adds a new reply stream to the set of tracked reply streams """
    cls.queue.put(("ADD", None, None, rs))
  @classmethod
  def del_reply_stream(cls, rs):
    """ deletes rs from the set of tracked reply streams """
    cls.queue.put(("DEL", None, None, rs))
  @classmethod
  def launch_worker(cls):
    """ launches a worker thread to process the items in the event queue.
      You MUST call this function once at initialization if you want events
      to be processed! """
    def worker():
      while True:
        op, is_target, msg, rs = cls.queue.get() # thread blocks until queue is non-empty
        if op == "SEND":
          for reply_stream in cls.reply_streams:
            if is_target(reply_stream):
              reply_stream.push(msg)
        elif op == "ADD":
          cls.reply_streams.append(rs)
        elif op == "DEL":
          for i, rs_i in enumerate(cls.reply_streams):
            if rs_i is rs:
              del cls.reply_streams[i]
              break
        else: assert(False)
    t = threading.Thread(target=worker)
    t.start()


def create_event_server_class(name, get_responder):
  return type(name, (EventServer,), {"get_responder": get_responder})





