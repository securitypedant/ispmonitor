import uuid, logging, config, json
from json import JSONEncoder
from datetime import datetime, date

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
    return timenow.strftime("%Y-%m-%d %H:%M:%S")
    
def writeDataFile(filename, content):
    with open('data/' + str(filename), 'w') as file:
        #json_content = json.dumps(encoder().encode(content))
        json_content = json.dumps(content.__dict__)
        file.write(json_content)

def createEvent(eventData, tracedHosts):
    event = monitorEvent(str(uuid.uuid4()))
    event.offlinetimedate = getDateNow()
    event.tracehosts = tracedHosts

    logging.debug(json.dumps(encoder().encode(event)))
    writeDataFile(str(date.today()) + "-" + event.id, event)

    return event.id

def updateEvent(filename, event):
    json_object = ""
    with open('data/' + filename, 'r') as json_file:
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

    with open('data/' + str(filename), 'w') as file:
        file.write(str(json_object))
