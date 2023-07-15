# ispmonitor
![Monitor screenshot](https://user-images.githubusercontent.com/11550089/228054835-cceb16aa-03b6-4665-8e00-0009cb987ec6.png)

This is a work in progress project. The final version will be a fully hostable ISP monitoring tool.

FIXME
- Fix windows Ping function
- Seperate scheduler log from monitor log in UX. Create a better log viewer for the scheduler log.
- Do I need to run speedtest on app startup?
- Improve tools page formatting
- Reverse order of data in graph
- Secure Redis connection with username/pass and store securely in Flask
- Update setting of secret key for app, storing in env variable

TODO
Version 1.0 Release
- Create docs and setup.sh
- Test all scenarios
- Group events by day in an expandable tree. Total up outage time per day at the high level.

Future release
- Use SSE to keep UX up to date in real time.
- Button to create speedtest report.
    - As a PDF
    - With a graph and speed test history
    - Allow week/month reports.
- Improve monitor ping to average out the hosts latency. Maybe store all the real values, but when graphing, build an average.
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
