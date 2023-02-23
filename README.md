# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
- Add list of network devices used for internet and include in outage check
    - DNS, router, firewall etc
    - Goal is to be able to determine why the internet is not available. Is your router down? DNS failure?
- Add config edit in UX
- Make speedtest an AJAX request
    - Have the UX show a wait while the request is processed.
    https://subscription.packtpub.com/book/web-development/9781783983407/4/ch04lvl1sec36/dealing-with-xhr-requests
    https://javascript.plainenglish.io/how-to-form-submissions-with-flask-and-ajax-dfde9891c620
- Improve logic for detecting an outage.
    - Possible a speedtest is blocking the scheduler.
- Improve logging
    - Sort logs on homepage by date
    - Improve the log.html view
- Graph uptime/ping times
    - Selector to choose timeframe. Day, week, month
    https://blog.heptanalytics.com/flask-plotly-dashboard/
    https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f 
- Add filter / search to log viewer
- Improve UX for event viewing
    - Add visual trace route (https://python.plainenglish.io/python-traceroute-with-a-visualization-like-in-the-hacker-movie-scene-179abcb74dc8)
    - Add button to download event details to send to someone via email
- Update online status dynamically without page refresh
- Add SMS notifications of outages (how would this work when the internet is down?)
- Add database support (MySQL, MongoDB)
- Fix MonitorISP to run standalone
- Create setup for running on a Raspberry Pi 4 B 