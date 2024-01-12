
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
var tabeaterEventSource = new EventSource("/events/"); // global event source variable
var eventCanary = 2; // global event canary variable to let us know if events are coming

function setEventSourceCallback() {
  tabeaterEventSource.onmessage = function(event) {
    eventCanary = 0;
    var sessions_div = document.getElementById("sessions");
    sessions_div.innerHTML = event.data;
  };
}


/////////////////////
// Initialization: //
/////////////////////


document.addEventListener("visibilitychange", () => {
  // On a visibility change, we should refresh the tab data
  // It's also a good opportunity to make sure our event source still works
  if (!document.hidden) {
    eventCanary = 1; // set event canary to 1, it should be cleared by the refresh
    refresh();
    setTimeout(function() {
      if (eventCanary != 0) {
        // event source maybe got disconnected, we need to recreate it
        console.log("Recreating EventSource '/events/'.");
        tabeaterEventSource = new EventSource("/events/");
        setEventSourceCallback();
        refresh(); // now we reiterate our refresh
      }
    }, 500); // [ms]
  }
});

// we should set the event source callback in our initial setup:
setEventSourceCallback();



