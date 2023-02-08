import uuid, logging, config
from datetime import datetime

def writeData(content):
    with open('data/events.csv', 'a') as file:
        file.write(content)

def createEvent(eventData):
    eventID = uuid.uuid4()
    current_time = datetime.now()
    dataToWrite = str(eventID) + "," + current_time.strftime(config.dateTimeFormat) + "," + str(eventData + "\n")

    logging.debug(dataToWrite)
    writeData(dataToWrite)

    return eventID
