from html import escape

# TODO: remove these lines
# hint for interactivity:
# <button onclick="js();"> TEXT </button>

def tab_to_html(tab):
  return "".join([
    '<div class="tab">',
    '<a href="%s">' % tab.url,
    '<img src="%s" class="icon"/> ' % tab.image,
    escape(tab.title),
    '</a> </div>\n',
  ])

def render_session(session):
  return ''.join([
    '<div class="session">',
    '<p>%s</p>' % escape(session.name),
    *[tab_to_html(tab) for tab in session.tabs],
    '</div>',
  ])

def render_sessions(sessions):
  # Note that it's important that the output contains no newlines!
  # This is because newlines are significant for the EventSource functionality
  # https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
  return ''.join([render_session(sess) for sess in sessions])



