# ispmonitor

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

TODO
Version 1.0 Release
- Create docs and setup.sh
- Reverse order of data in graph
- Test all scenarios

Future release
- Use SSE to keep UX up to date in real time.
- Allow deletion of events and logs from the UX.
- Button to create speedtest report.
    - As a PDF
    - With a graph and speed test history
    - Allow week/month reports.

- Allow a Notes field on an event.
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