import uuid, logging, config as config, json, os, logging
from json import JSONEncoder
from datetime import datetime, date
import json, os
from config import get_configValue

logger = logging.getLogger(config.loggerName)

class monitorEvent:
    def __init__(self, id):
        self.id = id
        self.offlinetimedate = ""
        self.onlinetimedate = ""
        self.downtime = 0
        self.onlineping = 0
        self.downspeed = 0
        self.upspeed = 0
        self.tracehosts = []

    def __str__(self):
        return (json.dumps(self))

class encoder(JSONEncoder):
    def default(self, o):
            return o.__dict__

def getDateNow():
    timenow = datetime.now()
    return timenow.strftime(get_configValue("datetimeformat"))
    
def writeEventsFile(filename, content):
    with open('events/' + str(filename), 'w') as file:
        json_content = json.dumps(content.__dict__)
        file.write(json_content)

def createEvent(eventData, tracedHosts):
    event = monitorEvent(str(uuid.uuid4()))
    event.offlinetimedate = getDateNow()
    event.tracehosts = tracedHosts

    logger.debug(json.dumps(encoder().encode(event)))
    writeEventsFile(str(date.today()) + "-" + event.id, event)

    return event.id

def getEvent(filename):
    with open('events/' + filename, 'r') as json_file:
        # Reading from json file
        event = json.load(json_file)

    return event

def updateEvent(filename, event):
    json_object = ""
    # FIXME Handle files not existing.
    with open('events/' + filename, 'r') as json_file:
        # Reading from json file
        json_object = json.load(json_file)
        
    json_object["onlineping"] = event.onlineping
    json_object["downspeed"] = event.downspeed
    json_object["upspeed"] = event.upspeed
    json_object["onlinetimedate"] = getDateNow()

    # Figure out downtime
    offlineStart = datetime.strptime(json_object["offlinetimedate"], "%Y-%m-%d %H:%M:%S")

    downtime = datetime.now() - offlineStart
    downtimeSeconds = downtime.total_seconds()
    json_object["downtime"] = downtimeSeconds

    with open('events/' + str(filename), 'w') as file:
        file.write(str(json_object))

def storeMonitorValue(type, value):
    # Check if data folder exists, if not, create it.
    dictItem = {getDateNow():value}
    with open('graphdata/' + type + '.json', 'a') as file:
        json.dump(dictItem, file)
        file.write("\n")

def readMonitorValues(type):
    with open('graphdata/' + type + '.json') as file:
        dictOfValues = [json.loads(line) for line in file]
    return dictOfValues

def getLastSpeedTest():
    try:
        with open('graphdata/speedTestResult.json') as file:
            for line in file:
                pass
            dictLastCheck = json.loads(line)
        return dictLastCheck
    except:
        return {0:0}
        