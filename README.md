# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
- Add exception catching to all external calls, i.e. Speedtests.
- Allow a Notes field on an event.
- Move as much config data into redis, avoiding file reads.
- In config, switch for enable/pause/disable scheduled jobs.
- Check if redis server is running and fail gracefully.
- Improve monitor ping to average out the hosts latency. Maybe store all the real values, but when graphing, build an average.
- Show in UX what the server is currently doing. i.e. speed test, checking internet, etc
    - https://www.velotio.com/engineering-blog/how-to-implement-server-sent-events-using-python-flask-and-react
    - https://github.com/singingwolfboy/flask-sse
- Setup Redis
    - Secure with username/pass and store securely in Flask
- Add list of network devices used for internet and include in outage check
    - DNS, router, firewall etc
    - Goal is to be able to determine why the internet is not available. Is your router down? DNS failure?
    - Tools
        - https://psutil.readthedocs.io/en/latest/
- Make speedtest an AJAX request
    - Have the UX show a wait while the request is processed.
    https://subscription.packtpub.com/book/web-development/9781783983407/4/ch04lvl1sec36/dealing-with-xhr-requests
    https://javascript.plainenglish.io/how-to-form-submissions-with-flask-and-ajax-dfde9891c620
- Improve logic for detecting an outage.
    - Possible a speedtest is blocking the scheduler.
- Improve logging
    - Sort logs on homepage by date
    - Improve the log.html view
    - Add filter / search to log viewer
- Graph uptime/ping times
    - Selector to choose timeframe. Day, week, month
    https://blog.heptanalytics.com/flask-plotly-dashboard/
    https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f 
- Improve UX for event viewing
    - Add visual trace route (https://python.plainenglish.io/python-traceroute-with-a-visualization-like-in-the-hacker-movie-scene-179abcb74dc8)
    - Add button to download event details to send to someone via email
- Add SMS notifications of outages (how would this work when the internet is down?)
- Add database support (MySQL, MongoDB)
- Create setup for running on a Raspberry Pi 4 B 