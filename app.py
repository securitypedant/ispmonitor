import os, json
from datetime import datetime
from flask import Flask, render_template, request
from config import set_configValue, get_configValue
from apscheduler.schedulers.background import BackgroundScheduler

from main import monitorISP

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(monitorISP, 'interval', seconds=5)

app = Flask(__name__)

def getOnlineStatus():
    status = get_configValue("currentstate")
    if status == "online":
        online = True
    else:
        online = False
        
    return online

def createEventDict(file):
    with open('data/' + file, 'r') as event:
        eventdict = eval(event.read())
        eventdict['filename'] = file
        eventdict['downtimeformatted'] = str(eventdict['downtime']).split('.')[0]
    return eventdict

@app.route("/")
def home():
    dataFolder = "data"
    logFolder = "logs"
    eventfiles = []
    logfiles = []
    events = []
    for filename in os.listdir(dataFolder):
        path = os.path.join(dataFolder, filename)
        if os.path.isfile(path):
            eventfiles.append(filename)

    for filename in os.listdir(logFolder):
        path = os.path.join(logFolder, filename)
        if os.path.isfile(path):
            logfiles.append(filename)

    # Get data from each event
    for file in eventfiles:
        events.append(createEventDict(file))

    return render_template(
        "home.html",
        online=getOnlineStatus(),
        events=events,
        logfiles=logfiles
    )

@app.route("/log")
def log():
    logfile = request.args.get("logid")
    with open('logs/' + str(logfile), 'r') as file: 
        lines = file.readlines()
        return render_template("log.html", lines=lines, logfilename=logfile, online=getOnlineStatus())

@app.route("/event")
def event():
    eventid = request.args.get("eventid")
    eventdict = createEventDict(eventid)
    return render_template("event.html", event=eventdict, online=getOnlineStatus())


@app.route("/api/data")
def get_data():
    with open('data/2023-02-09-6c4ec0af-4e0b-4c89-a17d-f520b52e3ec4', 'r') as file:
            # Reading from json file
            event = file.read()
            #event = json.load(json_file)
    return event