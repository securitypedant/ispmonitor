# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
Version 1.0 Release
- Improve overall UX
    - https://www.w3schools.com/bootstrap5/index.php
- Test all scenarios
- Add to connection monitor the first hop.
- Add exception catching to all external calls, i.e. Speedtests.
- In config, switch for enable/pause/disable scheduled jobs.
- in config, set logging level.
- Show in UX what the server is currently doing. i.e. speed test, checking internet, etc
    - https://www.velotio.com/engineering-blog/how-to-implement-server-sent-events-using-python-flask-and-react
    - https://github.com/singingwolfboy/flask-sse
- Add list of network devices used for internet and include in outage check
    - DNS, router, firewall etc
    - Goal is to be able to determine why the internet is not available. Is your router down? DNS failure?
    - Tools
        - https://psutil.readthedocs.io/en/latest/
- Improve logic for detecting an outage.
    - Possible a speedtest is blocking the scheduler.

Future release
- Button to create speedtest report.
    - As a PDF
    - With a graph and speed test history
    - Allow week/month reports.

- Allow a Notes field on an event.
- Check if redis server is running and fail gracefully.
- Improve monitor ping to average out the hosts latency. Maybe store all the real values, but when graphing, build an average.
- Setup Redis
    - Secure with username/pass and store securely in Flask
- Improve logging
    - Sort logs on homepage by date
    - Improve the log.html view
    - Add filter / search to log viewer
- Improve UX for event viewing
    - Add visual trace route (https://python.plainenglish.io/python-traceroute-with-a-visualization-like-in-the-hacker-movie-scene-179abcb74dc8)
    - Add button to download event details to send to someone via email
- Add SMS notifications of outages (how would this work when the internet is down?)
- Add database support (MySQL, MongoDB)
- Create setup for running on a Raspberry Pi 4 B 