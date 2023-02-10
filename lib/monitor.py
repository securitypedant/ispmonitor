import logging, config
from lib.network import traceroute, pinghost, runSpeedtest

logger = logging.getLogger(config.loggerName)

def checkConnection(hosts):
    failedHosts = 0

    for host in hosts:
    # Ping target to determine if network is available.
        logger.debug("Pinging " + host)
        pingReturn = pinghost(host)

        if pingReturn == 0:
            # Host is reachable
            logger.debug("Success reaching " + host)
        else:
            logger.error("Unable to reach " + host + " Ping return code:" + str(pingReturn))
            failedHosts = failedHosts + 1

    if failedHosts > 0:
        return False
    else:
        return True