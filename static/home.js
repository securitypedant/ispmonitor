window.onload=function(){

    if (isSpeedTestRunning) {
      document.getElementById('speedtest_button').disabled = true;
      document.getElementById('speedtest_button').textContent = "Speedtest Running...";
    }
    document.getElementById('speedtest_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/runspeedtest', true);
      xhr.onload = function() {
        var result = JSON.parse(xhr.responseText);
        document.getElementById('speedtest_result').innerHTML = result;
        document.getElementById('speedtest_button').textContent = "Run Speedtest";
        document.getElementById('speedtest_button').disabled = false;
      };
      xhr.send();
      document.getElementById('speedtest_button').disabled = true;
      document.getElementById('speedtest_button').textContent = "Speedtest Running...";
    });
    document.getElementById('test_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/test', true);
      xhr.send();
    });    
    var latencydropdown = document.getElementById('latencyrange');
    latencydropdown.addEventListener('change', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/getgraphdata?dropdownValue=' + this.value + '&graphType=latency', true);
        // xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.onreadystatechange = function() {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                // Update the plot with the new data returned from the server
                var updatedData = JSON.parse(this.responseText);
                Plotly.newPlot('latencychart',updatedData,{});
            }
        };
        xhr.send();
    });
    var speedrangedropdown = document.getElementById('speedrange');
    speedrangedropdown.addEventListener('change', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/getgraphdata?dropdownValue=' + this.value + '&graphType=speed', true);
        // xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.onreadystatechange = function() {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                // Update the plot with the new data returned from the server
                var updatedData = JSON.parse(this.responseText);
                Plotly.newPlot('speedchart',updatedData,{});
            }
        };
        xhr.send();
    });
  }


  