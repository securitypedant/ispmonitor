import uuid, logging, config, json
from json import JSONEncoder
from datetime import datetime, date

class monitorEvent:
    def __init__(self, id, offlinetimedate):
        self.id = id
        self.offlinetimedate = offlinetimedate
        self.onlinetimedate = ""
        self.onlineping = 0
        self.downspeed = 0
        self.upspeed = 0

class encoder(JSONEncoder):
    def default(self, o):
            return o.__dict__

def appendDataFile(filename, content):
    with open('data/' + str(filename), 'a') as file:
        json_content = json.dumps(encoder().encode(content))
        file.write(json_content + "\n")

def createEvent(eventData):
    event = monitorEvent(str(uuid.uuid4()), str(datetime.now()))

    logging.debug(event)
    appendDataFile(str(date.today()) + "-" + event.id, event)

    return event.id

def updateEvent(filename, event):
    with open(filename, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
        print (json_object)
