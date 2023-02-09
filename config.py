import yaml, platform

configFile = "config.yaml"
with open(configFile, 'r') as stream:
    config = yaml.safe_load(stream)

global dateTimeFormat, targetHosts, osType
dateTimeFormat = config["datetimeformat"]
targetHosts = config["hosts"]
currentState = config["currentstate"]
eventID = config["eventid"]
eventDate = config["eventdate"]


osType = platform.system()