import logging, config

from lib.network import traceroute, runSpeedtest
from lib.monitor import checkConnection, set_configValue
from lib.datastore import createEvent, updateEvent
from datetime import datetime, date
from lib.datastore import monitorEvent

# Constants and config
loggingLevel = logging.DEBUG
offlineTime = datetime.now()
eventID = ""
eventDate = ""

# Setup logging file
logging.basicConfig(filename='monitor.log', format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8', level=loggingLevel)
logging.debug("Attempting to reach " + str(config.targetHosts))

# Check connection.
if checkConnection(config.targetHosts):
    # We are online
    logging.debug("We can reach all monitored hosts")
    # Did we just come back online since previous check?
    if config["currentstate"] == "offline":
        logging.debug("We have just reconnected")

        reconnectTime = datetime.now()
        downtime = reconnectTime - offlineTime

        # Set currentstate to online
        set_configValue(config.configFile, "currentstate", "online")
        # Run speedtest
        speedTest = runSpeedtest()

        event = monitorEvent()
        event.onlineping = speedTest.results.ping
        event.downspeed = speedTest.results.download
        event.upspeed = speedTest.results.upload

        # Update event
        updateEvent(str(eventDate) + "-" + str(eventID), event)
    
else:
    # We are offline
    logging.debug("We do not have a valid internet connection!")

    # Change state to offline
    set_configValue(config.configFile, "currentstate", "offline")
    eventID = createEvent("offline")
    eventDate = date.today()

    # Record offline stats
    offlineTime = datetime.now()

    # Traceroute to determine what might be failing.

   
 

"""
    if pingReturn == 0:
        # Host is reachable
        logging.info("Success reaching " + host)
    else:
        # Host is not reachable
        
        tracedHosts = traceroute(host)
        logging.info("Traced hosts " + str(tracedHosts))
        logging.info(runSpeedtest())
"""