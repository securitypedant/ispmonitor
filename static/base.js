window.addEventListener("load",function(event) {
  if (isSpeedTestRunning) {
    document.getElementById('speedtest_button').disabled = true;
    document.getElementById('speedtest_button').innerHTML = "<span class='spinner-border spinner-border-sm'></span> Speedtest Running...";
  }

  document.getElementById('speedtest_button').addEventListener('click', function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/ajax/runspeedtest', true);
    xhr.onload = function() {
      var result = JSON.parse(xhr.responseText);
      document.getElementById('speedtest_result').innerHTML = result;
      document.getElementById('speedtest_button').textContent = "Run Speedtest";
      document.getElementById('speedtest_button').disabled = false;
      document.getElementById('speedtest-indicator').style.color = "orange";
    };
    xhr.send();
    document.getElementById('speedtest_button').disabled = true;
    document.getElementById('speedtest_button').innerHTML = "<span class='spinner-border spinner-border-sm'></span> Speedtest Running...";
    document.getElementById('speedtest-indicator').style.color = "green";
    
  });
},false);   