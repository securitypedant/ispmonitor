import yaml, platform
import logging

from flask import g
from datetime import datetime
from lib.datastore import db_connect, get_db_connection_data

global dateTimeFormat, targetHosts, osType, loggerName

loggerName = "monitor"
logger = logging.getLogger(loggerName)
osType = platform.system()

def setup_config():
    # Check to see if the database has a valid config, if not, default values.
    db = db_connect(get_db_connection_data(), get_file_config_value("mongoDbName"))
    if not read_db_value("config", ):
        write_db_value("config", )


def getDateNow(DATE_FORMAT) -> str:
    timenow = datetime.now()
    return timenow.strftime(DATE_FORMAT)

def write_db_value(collection, key, value):    
    db = db_connect(get_db_connection_data(), get_file_config_value("mongoDbName"))
    configData = db[collection]
    configData.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)
    if "db" not in g:
        db.close()

def read_db_value(collection, key):
    db = db_connect(get_db_connection_data(), get_file_config_value("mongoDbName"))
    config_collection = db[collection]
    config = config_collection.find_one({"_id": key})
    return config["value"] if config else None


def set_file_config_value(key, value):
    with open(configFile) as f:
        doc = yaml.safe_load(f)
    doc[key] = value

    with open(configFile, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)

def get_file_config_value(key):
    try:
        with open(configFile) as f:
            doc = yaml.safe_load(f)

            return doc[key]
    except:
        logger.debug("Problem with get_configValue for " + key)