import logging, config as config, signal, sys, getopt, time, os
import logging.handlers as handlers

from lib.network import traceroute, runSpeedtest
from lib.monitor import checkConnection
from config import set_configValue, get_configValue
from lib.datastore import createEvent, updateEvent, monitorEvent, getEvent
from datetime import datetime, date

class SignalHandler:
    shutdown_requested = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)

    def request_shutdown(self, *args):
        print('Request to shutdown received, stopping')
        logger.info('Request to shutdown received, stopping')
        self.shutdown_requested = True

    def can_run(self):
        return not self.shutdown_requested

# Constants and config
loggingLevel = logging.INFO
eventID = ""
eventDate = ""
traceTargetHost = "8.8.8.8"
signal_handler = SignalHandler()

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

def monitorISP():
    hosts = get_configValue("hosts")
    logger.debug("Attempting to reach " + str(hosts))
    # Check connection.
    if checkConnection(hosts):
        # We are ONLINE
        logger.info("Successfuly pinged " + str(hosts))
        
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
        logger.info("Unable to connect to internet.")
        
        # Were we previously offline?
        if get_configValue("currentstate") == "offline":
            event = getEvent(get_configValue("eventdate") + "-" + get_configValue("eventid"))
            logger.debug("We are still offline since " + event["offlinetimedate"])
        else:
            # Change state to offline
            set_configValue("currentstate", "offline")

            # Traceroute to determine what might be failing.
            tracedHosts = traceroute(traceTargetHost)
            logger.info("Traced hosts " + str(tracedHosts))

            # Store data
            eventID = createEvent("offline", tracedHosts)
            set_configValue("eventid", eventID)
            set_configValue("eventdate", str(date.today()))
        
    logger.info("----------------------------------------------------------------------------------------------------")

def main():
    opts, args = getopt.getopt(sys.argv[1:], "s")
    if len(sys.argv) > 1:
        print("Starting ISPMonitor as a service.")
        logger.info("Starting ISPMonitor as a service.")
        for opt, arg in opts:
            if opt == "-s":
                # Run as a service
                while signal_handler.can_run():
                    monitorISP()
                    time.sleep(10)
    else:
        print("Running ISPMonitor once.")
        logger.debug("Running ISPMonitor once.")        
        monitorISP()          

if __name__ == "__main__":
    main()

