# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
Version 1.0 Release
- Create docs and setup.sh
- Reverse order of data in graph
- Improve overall UX
    - https://www.w3schools.com/bootstrap5/index.php
    - https://designmodo.com/bootstrap-5-layout/
- Test all scenarios
- Add to connection monitor the first hop.
- Add exception catching to all external calls, i.e. Speedtests.
- Show in UX what the server is currently doing. i.e. speed test, checking internet, etc
    - https://www.velotio.com/engineering-blog/how-to-implement-server-sent-events-using-python-flask-and-react
    - https://github.com/singingwolfboy/flask-sse

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