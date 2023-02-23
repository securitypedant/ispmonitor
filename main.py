import logging, config as config, os
import logging.handlers as handlers

from lib.network import traceroute, runSpeedtest
from lib.monitor import checkConnection
from config import set_configValue, get_configValue
from lib.datastore import createEvent, updateEvent, monitorEvent, getEvent, storeMonitorValue
from datetime import date, datetime
from flask import session, Flask, g

# Constants and config
loggingLevel = logging.DEBUG
eventID = ""
eventDate = ""
traceTargetHost = "8.8.8.8"

# Setup logging file
# Check if data folder exists, if not, create it.
if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger(config.loggerName)
logger.setLevel(loggingLevel)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logHandler = handlers.TimedRotatingFileHandler('logs/monitor.log', when='D', interval=1, backupCount=31)
logHandler.setLevel(loggingLevel)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = Flask(__name__)

def scheduledSpeedTest():
    logger.debug("Running speed test")
    speedTestResults = runSpeedtest()
    speedTestResultsList = [round(speedTestResults.results.download / 1000 / 1000, 1), round(speedTestResults.results.upload / 1000 / 1000, 1)]

    storeMonitorValue('speedtestResult', speedTestResultsList)

def monitorISP():
    hosts = get_configValue("hosts")
    logger.debug("Attempting to reach " + str(hosts))
    # Check connection.
    set_configValue("lastcheck", datetime.now().strftime(get_configValue('datetimeformat')))
    checkResult = checkConnection(hosts)
    if checkResult:
        # We are ONLINE
        logger.info("Connection test success:Pinged hosts " + str(hosts))
        storeMonitorValue('pingResult', checkResult)

        # Did we just come back online since previous check?
        if get_configValue("currentstate") == "offline":
            logger.debug("Internet has reconnected.")

            # Set currentstate to online
            set_configValue("currentstate", "online")
            # Run speedtest
            speedTest = runSpeedtest()
            event = monitorEvent(get_configValue("eventid"))
            event.onlineping = speedTest.results.ping
            event.downspeed = speedTest.results.download
            event.upspeed = speedTest.results.upload

            # Update event
            updateEvent(str(get_configValue("eventdate")) + "-" + get_configValue("eventid"), event)
    else:
        # We are OFFLINE
        # Were we previously offline?
        if get_configValue("currentstate") == "offline":
            event = getEvent(get_configValue("eventdate") + "-" + get_configValue("eventid"))
            logger.error("We are still offline:Internet connection down since " + event["offlinetimedate"])
        else:
            # Change state to offline
            set_configValue("currentstate", "offline")

            # Traceroute to determine what might be failing.
            tracedHosts = traceroute(traceTargetHost)
            logger.error("Connection test failed:Traced hosts " + str(tracedHosts))

            # Store data
            eventID = createEvent("offline", tracedHosts)
            set_configValue("eventid", eventID)
            set_configValue("eventdate", str(date.today()))
        
