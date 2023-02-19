# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
- Add config edit in UX
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