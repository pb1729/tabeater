
function send_req(type, url) {
  var request = new XMLHttpRequest();
  request.open(type, url, true);
  request.send();
}

function refresh() {
  send_req('GET', '/refresh/');
}

function del_sess(sess_id) {
  send_req('DELETE', '/session/' + sess_id);
}

function del_tab(tab_id) {
  send_req('DELETE', '/tab/' + tab_id)
}

function open_all_tabs(sess_id) {
  var session_div = document.getElementById("" + sess_id);
  session_div.childNodes.forEach(node => {
    if (node.className == "tab") {
      try {
        var url = node.getAttribute("taburl");
        window.open(url);
      } catch(err) {
        console.log(err);
      }
    }
  });
}


// set up the event source and UI updating
let eventSource = new EventSource("/events/");

eventSource.onmessage = function(event) {
  var sessions_div = document.getElementById("sessions");
  sessions_div.innerHTML = event.data;
};


