import yaml

configFile = "config.yaml"
with open(configFile, 'r') as stream:
    config = yaml.safe_load(stream)

global dateTimeFormat, targetHosts
dateTimeFormat = config["datetimeformat"]
targetHosts = config["hosts"]
currentState = config["currentstate"]
eventID = config["eventid"]