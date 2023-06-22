window.onload=function(){
    /*
    document.getElementById('test_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/test', true);
      xhr.send();
    });
    */
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


  