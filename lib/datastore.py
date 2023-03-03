import logging, config as config, json
from json import JSONEncoder
from datetime import datetime
import json, pathlib
from lib.redis_server import getRedisConn

logger = logging.getLogger(config.loggerName)
redis_conn = getRedisConn()

class encoder(JSONEncoder):
    def default(self, o):
            return o.__dict__

def getDateNow():
    timenow = datetime.now()
    return timenow.strftime(redis_conn.get('datetimeformat'))

def createEvent(eventDict):
    
    logger.debug(json.dumps(encoder().encode(eventDict)))
    with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / eventDict['id'], 'w') as file:
        json_content = json.dumps(eventDict)
        file.write(json_content)

    return

def getEvent(filename):
    with open(pathlib.Path(redis_conn.get('eventsdatafolder'))  / filename, 'r') as json_file:
        # Reading from json file
        event = json.load(json_file)

    return event

def updateEvent(filename, event):
    json_object = ""
    # FIXME Handle files not existing.
    with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / filename, 'r') as json_file:
        # Reading from json file
        json_object = json.load(json_file)
        
    json_object['onlineping'] = event['onlineping']
    json_object['downspeed'] = event['downspeed']
    json_object['upspeed'] = event['upspeed']
    json_object['online_timedate'] = getDateNow()

    # Figure out downtime
    offlineStart = datetime.strptime(json_object["offline_timedate"], "%Y-%m-%d %H:%M:%S")

    downtime = datetime.now() - offlineStart
    downtimeSeconds = downtime.total_seconds()
    json_object["total_downtime"] = downtimeSeconds

    with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / str(filename), 'w') as file:
        json_towrite = json.dumps(json_object)
        file.write(str(json_towrite))
        
def createEventDict(file):
    with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / file, 'r') as event:
        eventdict = json.load(event)
        eventdict['filename'] = file
        eventdict['downtimeformatted'] = str(eventdict['total_downtime']).split('.')[0]
    return eventdict
        
def storeMonitorValue(type, value):
    # Check if data folder exists, if not, create it.
    dictItem = {getDateNow():value}
    type = type + '.json'
    with open(pathlib.Path(redis_conn.get('graphdatafolder')) / type, 'a') as file:
        json.dump(dictItem, file)
        file.write("\n")

def readMonitorValues(type):
    type = type + '.json'
    try:
        with open(pathlib.Path(redis_conn.get('graphdatafolder')) / type) as file:
            dictOfValues = [json.loads(line) for line in file]
    except Exception as e:
        return False
    else:
        return dictOfValues

def getLastSpeedTest():
    try:
        dictLastCheck = json.loads(redis_conn.get('lastspeedtest'))
        #with open(pathlib.Path(redis_conn.get('graphdatafolder')) / 'speedTestResult.json') as file:
        #    for line in file:
        #        pass
        #    dictLastCheck = json.loads(line)
        return dictLastCheck
    except:
        return {0:0}
        