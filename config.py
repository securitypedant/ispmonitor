import yaml, platform

global dateTimeFormat, targetHosts, osType, loggerName, eventID, eventDate
configFile = "config.yaml"

def set_configValue(key, value):
    with open(configFile) as f:
        doc = yaml.safe_load(f)

    doc[key] = value

    with open(configFile, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def get_configValue(key):
    with open(configFile) as f:
        doc = yaml.safe_load(f)

        return doc[key]

#dateTimeFormat = config["datetimeformat"]
#eventID = config["eventid"]
#eventDate = config["eventdate"]
loggerName = "monitor"
osType = platform.system()