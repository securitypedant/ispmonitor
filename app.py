import ajax, redis
import os, yaml, plotly, json, datetime
from flask import Flask, render_template, request, redirect, url_for
from lib.datastore import readMonitorValues, getLastSpeedTest
from apscheduler.schedulers.background import BackgroundScheduler
from config import get_configValue, set_configValue
from main import monitorISP, scheduledSpeedTest

import pandas as pd
import plotly.express as px
import redis

app = Flask(__name__)
# Details on the Secret Key: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
# NOTE: The secret key is used to cryptographically-sign the cookies used for storing the session data.
app.secret_key = 'BAD_SECRET_KEY'

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(monitorISP, 'interval', seconds=get_configValue("pollfreq"), max_instances=1)
#scheduler.add_job(scheduledSpeedTest, 'interval', seconds=get_configValue("speedtestfreq"), max_instances=1)

redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
redis_conn.set('isspeedtestrunning', 'no')
redis_conn.set('currentstate', 'online')

@app.before_first_request
def appStartup():
    # Check if required folders exist.
    if not os.path.exists("logs"):
        os.makedirs("logs")

    if not os.path.exists("events"):
        os.makedirs("events")

    if not os.path.exists("graphdata"):
        os.makedirs("graphdata")

    # Create data files if they don't exist.
    if not os.path.isfile('graphdata/speedtestResult.json'):
        with open('graphdata/speedtestResult.json', 'w'):
            pass

    if not os.path.isfile('graphdata/pingResult.json'):
        with open('graphdata/pingResult.json', 'w'):
            pass

@app.context_processor
def getOnlineStatus():
    status = redis_conn.get('currentstate')
    if status == 'online':
        online = True
    else:
        online = False
        
    return dict(onlinestatus=online)

@app.context_processor
def lastcheckdate():
    lastcheck = redis_conn.get('lastcheck')
    return dict(lastcheckdate=lastcheck)

def createEventDict(file):
    with open('events/' + file, 'r') as event:
        eventdict = eval(event.read())
        eventdict['filename'] = file
        eventdict['downtimeformatted'] = str(eventdict['downtime']).split('.')[0]
    return eventdict

# ------------------ ROUTES  ------------------ 
app.add_url_rule('/ajax/runspeedtest', view_func=ajax.ajaxspeedtest)
app.add_url_rule('/ajax/listspeedtestservers', view_func=ajax.ajaxListSpeedtestServers)

@app.route("/", methods=['GET'])
def render_home():
    dataFolder = "events"
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

    latencyData = readMonitorValues('pingResult')

    xVals = []
    yVals = []

    for latencyDict in latencyData:
        key = list(latencyDict.keys())
        value = list(latencyDict.values())
        xVals.append(key[0])
        yVals.append(int(value[0]))

    latencyDF = pd.DataFrame({'Date/Time':xVals,'ms':yVals})
    ltfig = px.line(latencyDF, x='Date/Time', y='ms', title="Connection latency")
     
    ltfig.update_layout(
        title="Connection latency",
        yaxis_title="Latency in ms"
    )

    # Create graphJSON
    graphJSON = json.dumps(ltfig, cls=plotly.utils.PlotlyJSONEncoder)

    speedTestData = readMonitorValues('speedtestResult')
    stxVals = []
    stDownyVals = []
    stUpyVals = []

    for speedTestDict in speedTestData:
        key = list(speedTestDict.keys())
        value = speedTestDict[key[0]]
        stxVals.append(key[0])
        stDownyVals.append(int(value[0]))
        stUpyVals.append(int(value[1]))

    speedTestDF = pd.DataFrame({'Date/Time':stxVals,'Download':stDownyVals,'Upload':stUpyVals})
    stfig = px.line(speedTestDF, x='Date/Time', y=['Download','Upload'], title="Connection speed")

    stfig.update_layout(
        title="Connection speed",
        yaxis_title="Speed in MB/s",
        legend_title="Bandwidth"
    )     
    # Create graphJSON
    stgraphJSON = json.dumps(stfig, cls=plotly.utils.PlotlyJSONEncoder)

    lastSpeedTest = getLastSpeedTest()
    listLastSpeedTest = list(lastSpeedTest.values())[0]

    return render_template(
        "home.html",
        events=events,
        graphJSON=graphJSON,
        stgraphJSON=stgraphJSON,
        listLastSpeedTest=listLastSpeedTest,
        logfiles=logfiles
    )

@app.route("/log")
def log():
    logfile = request.args.get("logid")
    with open('logs/' + str(logfile), 'r') as file: 
        lines = file.readlines()
        return render_template("log.html", lines=lines, logfilename=logfile)

@app.route("/event")
def event():
    eventid = request.args.get("eventid")
    eventdict = createEventDict(eventid)
    return render_template("event.html", event=eventdict)

@app.route("/config", methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        #Enumerate form data into file.
        set_configValue("pollfreq", int(request.form['pollfreq']))
        set_configValue('speedtestfreq', int(request.form['speedtestfreq']))
        set_configValue('datetimeformat', request.form['datetimeformat'])
        set_configValue('speedtestserverid', request.form['speedtestserverid'])
        
        hostsList = request.form['hosts'].split('\r\n')
        hostsListClean = [item.strip() for item in hostsList]

        set_configValue('hosts', hostsListClean)

    with open('config.yaml', 'r') as configfile:
        configdict = yaml.safe_load(configfile)
    return render_template("config.html", configdict=configdict)

if __name__ == "__main__":
    app.run()