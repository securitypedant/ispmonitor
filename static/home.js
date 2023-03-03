window.onload=function(){
    document.getElementById('speedtest_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/runspeedtest', true);
      xhr.onload = function() {
        var result = JSON.parse(xhr.responseText);
        document.getElementById('speedtest_result').innerHTML = result;
      };
      xhr.send();
    });
    document.getElementById('test_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/test', true);
      xhr.onload = function() {
        var result = JSON.parse(xhr.responseText);
        document.getElementById('test_result').innerHTML = result;
      };
      xhr.send();
    });
    var latencydropdown = document.getElementById('latencyrange');
    latencydropdown.addEventListener('change', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/getgraphdata?dropdownValue=' + this.value, true);
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
  }