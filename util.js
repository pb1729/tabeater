
function send_req(type, url) {
  var request = new XMLHttpRequest();
  request.open(type, url, true);
  request.send();
}

let eventSource = new EventSource("/events/");

eventSource.onmessage = function(event) {
  var sessions_div = document.getElementById("sessions");
  sessions_div.innerHTML = event.data;
};


