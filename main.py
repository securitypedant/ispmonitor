import logging, config, signal, sys, getopt

from lib.network import traceroute, runSpeedtest
from lib.monitor import checkConnection, set_configValue, get_configValue
from lib.datastore import createEvent, updateEvent, monitorEvent
from datetime import datetime, date

class SignalHandler:
    shutdown_requested = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)

    def request_shutdown(self, *args):
        print('Request to shutdown received, stopping')
        self.shutdown_requested = True

    def can_run(self):
        return not self.shutdown_requested

# Constants and config
loggingLevel = logging.DEBUG
eventID = ""
eventDate = ""
traceTargetHost = "8.8.8.8"
signal_handler = SignalHandler()

# Setup logging file
logging.basicConfig(filename='monitor.log', format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8', level=loggingLevel)

def monitorISP():
    logging.debug("Attempting to reach " + str(config.targetHosts))
    # Check connection.
    if checkConnection(config.targetHosts):
        # We are ONLINE
        logging.info("Successfuly pinged " + str(config.targetHosts))
        
        # Did we just come back online since previous check?
        if get_configValue(config.configFile, "currentstate") == "offline":
            logging.debug("We have just reconnected")

            # Set currentstate to online
            set_configValue(config.configFile, "currentstate", "online")
            # Run speedtest
            speedTest = runSpeedtest()
            event = monitorEvent(get_configValue(config.configFile, "eventid"))
            event.onlineping = speedTest.results.ping
            event.downspeed = speedTest.results.download
            event.upspeed = speedTest.results.upload

            # Update event
            updateEvent(str(config.eventDate) + "-" + config.eventID, event)
        
    else:
        # We are OFFLINE
        logging.debug("We do not have a valid internet connection!")
        
        # Were we previously offline?
        if get_configValue(config.configFile, "currentstate") == "offline":
            pass
        else:
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

def main():
    opts, args = getopt.getopt(sys.argv[1:], "s")
    if len(sys.argv) > 1:
        print("Starting ISPMonitor as a service.")
        logging.info("Starting ISPMonitor as a service.")
        for opt, arg in opts:
            if opt == "-s":
                # Run as a service
                while signal_handler.can_run():
                    monitorISP()
    else:
        print("Running ISPMonitor once.")
        logging.debug("Running ISPMonitor once.")        
        monitorISP()          

if __name__ == "__main__":
    main()

