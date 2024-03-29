from html import escape


def tab_to_html(tab):
  checked_str = "checked" if tab.state == 1 else ""
  lock_icon = "🔒" if tab.state == 1 else "🔓"
  return "".join([
    '<div class="tab" id="%d" taburl="%s">' % (tab.id, tab.url),
    '<button onclick="del_tab(%d)">❌</button> ' % tab.id,
    '%s<input type="checkbox" onclick="on_checkbox_click(this, \'%s\')" %s /> ' % (lock_icon, tab.id, checked_str),
    ' <a href="%s" target="_blank">' % tab.url,
    '<img src="%s" class="icon"/> ' % tab.image,
    escape(tab.title),
    '</a>',
    '</div>',
  ])

def render_session(session):
  return ''.join([
    '<div class="session" id="%d">' % session.id,
    '<p>',
    escape(session.name),
    ' || ',
    '<button onclick="del_sess(%d)">delete</button>' % session.id,
    ' || ',
    '<button onclick="open_all_tabs(%d)">open all</button>' % session.id,
    '</p>',
    *[tab_to_html(tab) for tab in session.tabs],
    '</div>',
  ])

def render_sessions(sessions):
  # Note that it's important that the output contains no newlines!
  # This is because newlines are significant for the EventSource functionality
  # https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
  return ''.join([render_session(sess) for sess in sessions])



