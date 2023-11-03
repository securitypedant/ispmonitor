import logging, lib.config as config, json, glob, os
from json import JSONEncoder
from datetime import datetime
import json, pathlib
from lib.redis_server import getRedisConn
from lib.config import get_file_config_value, getDateNow

from flask import g, current_app
from pymongo import MongoClient


def is_in_app_context():
    try:
        current_app._get_current_object()
        return True
    except RuntimeError:
        return False

class DBConnection:
    def __init__(self, host, port, username, password) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __str__(self):
        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"        

def get_db_connection_data():
    return DBConnection(
        get_file_config_value("mongoDbHost"),
        get_file_config_value("mongoDbPort"),
        get_file_config_value("mongoDbUser"),
        get_file_config_value("mongoDbPass")
    )

def db_connect(connection_details, database_name):
    db_client = MongoClient(str(connection_details))
    if is_in_app_context():
        if "db" not in g:
            g.db = db_client[database_name]
        return g.db
    else:
        db = db_client[database_name]
        return db

def db_close(db):
        db.close()

def set_db_config_value(db, key, value):
    configData = db['config']
    configData.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

def get_db_config_value(db, key):
    config_collection = db["config"]
    config = config_collection.find_one({"_id": key})
    return config["value"] if config else None

logger = logging.getLogger(config.loggerName)
redis_conn = getRedisConn()

class encoder(JSONEncoder):
    def default(self, o):
            return o.__dict__

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

def appendEvent(eventID, message, datetime, result, data):
    # redis_conn.get('last_eventid'), ["Host check during event", getDateNow(), result, checkResult[1]]
        with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / eventID, 'r') as json_file:
            # Reading from json file
            json_object = json.load(json_file)

            json_object['checks'].append([message, datetime, result, data])

        with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / str(eventID), 'w') as file:
            json_towrite = json.dumps(json_object)
            file.write(str(json_towrite))


def deleteEvent(eventid):
    os.remove(redis_conn.get('eventsdatafolder') + "/" + eventid)

def updateEvent(filename, event):
    json_object = ""
    # FIXME Handle files not existing.
    with open(pathlib.Path(redis_conn.get('eventsdatafolder')) / filename, 'r') as json_file:
        # Reading from json file
        json_object = json.load(json_file)
        
    json_object['onlineping'] = event['onlineping']
    json_object['downspeed'] = event['downspeed']
    json_object['upspeed'] = event['upspeed']
    json_object['online_timedate'] = event['online_timedate']
    json_object['currentState'] = event['currentState']
    if 'notes' in event:
        json_object['notes'] = event['notes']
    if 'reason' in event:
        json_object['reason'] = event['reason']
    
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
        if eventdict['currentState'] == 'online':
            eventdict['downtimeformatted'] = str(eventdict['total_downtime']).split('.')[0]

    return eventdict
        
def storeMonitorValue(type, value):
    now = datetime.now()
    dictItem = {"date":getDateNow(),"data":value}

    filename = str(now.date()) + "-" + type + '.json'
    with open(pathlib.Path(redis_conn.get('graphdatafolder')) / filename, 'a') as file:
        json.dump(dictItem, file)
        file.write("\n")

def readMonitorValues(type, range='hour'):
    if range == 'hour' or range == 'day':
        fileRange = str(datetime.now().date())
    else:
        fileRange = str(datetime.now().year) + "-" + datetime.now().strftime('%m')

    file_pattern = os.path.join(redis_conn.get('graphdatafolder') + '/' + fileRange + '*' + type + '.json')
    files = glob.glob(file_pattern)

    listOfValues = []

    for filename in files:
        with open(filename, 'r') as file:
            for line in file:
                listOfValues.append(json.loads(line))

    if listOfValues == []:
        sortedValues = {}
    else:
        sortedValues = sorted(listOfValues, key=lambda x: x["date"])

    return sortedValues

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
        