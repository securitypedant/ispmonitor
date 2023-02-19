import os, yaml, plotly, json
from flask import Flask, render_template, request, redirect, url_for
from config import get_configValue
from lib.datastore import readMonitorValues, getLastSpeedTest
from apscheduler.schedulers.background import BackgroundScheduler
from config import get_configValue
import pandas as pd
import plotly.express as px
from main import monitorISP, scheduledSpeedTest

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(monitorISP, 'interval', seconds=get_configValue("pollfreq"), max_instances=1)

scheduler.add_job(scheduledSpeedTest, 'interval', seconds=get_configValue("speedtestfreq"), max_instances=1)

app = Flask(__name__)

@app.context_processor
def getOnlineStatus():
    status = get_configValue("currentstate")
    if status == "online":
        online = True
    else:
        online = False
        
    return dict(onlinestatus=online)

@app.context_processor
def lastcheckdate():
    lastcheck = get_configValue("lastcheck")
    return dict(lastcheckdate=lastcheck)

def createEventDict(file):
    with open('data/' + file, 'r') as event:
        eventdict = eval(event.read())
        eventdict['filename'] = file
        eventdict['downtimeformatted'] = str(eventdict['downtime']).split('.')[0]
    return eventdict

@app.route("/", methods=['POST'])
def submit_home():
    if 'speedtest_button' in request.form:
        scheduledSpeedTest()

    return redirect(url_for('render_home'))

@app.route("/", methods=['GET'])
def render_home():
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

@app.route("/config")
def config():
    with open('config.yaml', 'r') as configfile:
        configdict = yaml.safe_load(configfile)
    return render_template("config.html", configdict=configdict)

if __name__ == "__main__":
    app.run(port=8000, debug=True)