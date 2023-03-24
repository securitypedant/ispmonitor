
  window.onload=function(){
    document.getElementById('checkinterface_button').addEventListener('click', function() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/ajax/checkinterface', true);
      xhr.onload = function() {
        var result = JSON.parse(xhr.responseText);
        // Get a reference to the HTML element where you want to display the data
        const container = document.getElementById("checkinterface_result");
        // Clear the contents of the container (optional)
        container.innerHTML = result;
      };
      xhr.send();
    });

    document.getElementById('checkdefaultroute_button').addEventListener('click', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/checkdefaultroute', true);
        xhr.onload = function() {
          var result = JSON.parse(xhr.responseText);
          // Get a reference to the HTML element where you want to display the data
          const container = document.getElementById("checkdefaultroute_result");
          // Clear the contents of the container (optional)
          container.innerHTML = result;
        };
        xhr.send();
      });

      document.getElementById('checkdns_button').addEventListener('click', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/checkdns', true);
        xhr.onload = function() {
          var result = JSON.parse(xhr.responseText);
          // Get a reference to the HTML element where you want to display the data
          const container = document.getElementById("checkdns_result");
          // Clear the contents of the container (optional)
          container.innerHTML = result;
        };
        xhr.send();
      });

      document.getElementById('traceroute_button').addEventListener('click', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/ajax/traceroute', true);
        xhr.onload = function() {
          document.getElementById('traceroute_button').disabled = false;
          var result = JSON.parse(xhr.responseText);
          // Get a reference to the HTML element where you want to display the data
          const container = document.getElementById("traceroute_result");
          // Clear the contents of the container (optional)
          container.innerHTML = result;
        };
        xhr.send();
        document.getElementById('traceroute_button').disabled = true;
      });      
  }
  
  