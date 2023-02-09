import logging, config

from lib.network import traceroute, runSpeedtest
from lib.monitor import checkConnection, set_configValue
from lib.datastore import createEvent, updateEvent, monitorEvent
from datetime import datetime, date

# Constants and config
loggingLevel = logging.DEBUG
eventID = ""
eventDate = ""
traceTargetHost = "8.8.8.8"

# Setup logging file
logging.basicConfig(filename='monitor.log', format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8', level=loggingLevel)
logging.debug("Attempting to reach " + str(config.targetHosts))

# Check connection.
if checkConnection(config.targetHosts):
    # We are online
    logging.debug("We can reach all monitored hosts")
    
    # Did we just come back online since previous check?
    if config.currentState == "offline":
        logging.debug("We have just reconnected")

        # Set currentstate to online
        set_configValue(config.configFile, "currentstate", "online")
        # Run speedtest
        speedTest = runSpeedtest()

        event = monitorEvent(config.eventID)
        event.onlineping = speedTest.results.ping
        event.downspeed = speedTest.results.download
        event.upspeed = speedTest.results.upload

        # Update event
        updateEvent(str(config.eventDate) + "-" + config.eventID, event)
    
else:
    # We are offline
    logging.debug("We do not have a valid internet connection!")

    # Change state to offline
    set_configValue(config.configFile, "currentstate", "offline")

    # Traceroute to determine what might be failing.
    tracedHosts = traceroute(traceTargetHost)
    logging.info("Traced hosts " + str(tracedHosts))

    # Store data
    eventID = createEvent("offline", tracedHosts)
    set_configValue(config.configFile, "eventid", eventID)
    set_configValue(config.configFile, "eventdate", str(date.today()))
    
logging.info("###########################################################################################################")