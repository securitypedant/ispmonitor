import logging, config as config
from lib.network import pinghost, ping3host
from ping3 import ping

logger = logging.getLogger(config.loggerName)

def checkConnection(hosts):
    failedHosts = 0

    for host in hosts:
    # Ping target to determine if network is available.
        logger.debug("Pinging " + host)
        # https://pypi.org/project/ping3/
        pingReturn = ping(host, unit='ms')

        if pingReturn:
            # Host is reachable
            logger.debug("Success reaching " + host)
        else:
            logger.error("Unable to reach " + host + " - DNS lookup failed" if not pingReturn else " - Host didn't reply")
            failedHosts = failedHosts + 1

    if failedHosts > 0:
        return False
    else:
        return str(pingReturn).split(".")[0]


