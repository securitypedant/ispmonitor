import yaml, platform
import logging

global dateTimeFormat, targetHosts, osType, loggerName, eventID, eventDate
configFile = "config.yaml"
loggerName = "monitor"
logger = logging.getLogger(loggerName)
osType = platform.system()

def set_configValue(key, value):
    with open(configFile) as f:
        doc = yaml.safe_load(f)
    doc[key] = value

    with open(configFile, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def get_configValue(key):
    try:
        with open(configFile) as f:
            doc = yaml.safe_load(f)

            return doc[key]
    except:
        logger.debug("Problem with get_configValue for " + key)