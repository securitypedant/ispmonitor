import logging, yaml
from lib.network import traceroute, pinghost, runSpeedtest

def checkConnection(hosts):
    failedHosts = 0
    
    for host in hosts:
    # Ping target to determine if network is available.
        logging.debug("Pinging " + host)
        pingReturn = pinghost(host)

        if pingReturn == 0:
            # Host is reachable
            logging.debug("Success reaching " + host)
        else:
            logging.error("Unable to reach " + host + " Ping return code:" + str(pingReturn))
            failedHosts = failedHosts + 1

    if failedHosts < len(hosts):
        return True
    else:
        return False

def set_configValue(file, key, value):
    with open(file) as f:
        doc = yaml.safe_load(f)

    doc[key] = value

    with open(file, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)
