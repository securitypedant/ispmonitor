import ajax, pathlib, humanize
import os, yaml, json
from datetime import datetime, timedelta
import logging, config as config
import logging.handlers as handlers

from flask import Flask, render_template, request, redirect, url_for
from lib.datastore import readMonitorValues, getLastSpeedTest, createEventDict
from lib.network import getLocalInterfaces, traceroute
from apscheduler.schedulers.background import BackgroundScheduler
from config import get_configValue, set_configValue
from jobs import scheduledCheckConnection, scheduledSpeedTest, scheduledCheckNetworkConfig
from lib.redis_server import getRedisConn
from lib.graphs import getLatencyGraphData, getSpeedtestGraphData

import redis

app = Flask(__name__)
# Details on the Secret Key: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
# NOTE: The secret key is used to cryptographically-sign the cookies used for storing the session data.
app.secret_key = 'BAD_SECRET_KEY'

# Setup logging file
logger = logging.getLogger(config.loggerName)
redis_conn = getRedisConn()

scheduler = BackgroundScheduler()
scheduler.start()
jobCheckConnection = scheduler.add_job(scheduledCheckConnection, 'interval', seconds=get_configValue("pollfreq"), max_instances=1)
jobSpeedTest = scheduler.add_job(scheduledSpeedTest, 'interval', seconds=get_configValue("speedtestfreq"), max_instances=1)
jobCheckNetConfig = scheduler.add_job(scheduledCheckNetworkConfig, 'interval', seconds=get_configValue("netconfigtestfreq"), max_instances=1)

if get_configValue("connectionmonitorjobstatus") == "pause":
    jobCheckConnection.pause()
if get_configValue("speedtestjobstatus") == "pause":
    jobSpeedTest.pause()
if get_configValue("checknetconfigjobstatus") == "pause":
    jobCheckNetConfig.pause()    

redis_conn.set('jobIDCheckConnection', jobCheckConnection.id)
redis_conn.set('jobIDSpeedTest', jobSpeedTest.id)
redis_conn.set('jobIDCheckNetConfig', jobCheckNetConfig.id)

@app.before_first_request
def appStartup():

    logger.setLevel(get_configValue("logginglevel"))
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    logHandler = handlers.TimedRotatingFileHandler(redis_conn.get('logsdatafolder') + '/monitor.log', when='D', interval=1, backupCount=31)
    logHandler.setLevel(get_configValue("logginglevel"))
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # Check if required folders exist.
    if not os.path.exists("logs"):
        os.makedirs("logs")

    if not os.path.exists("events"):
        os.makedirs("events")

    if not os.path.exists("graphdata"):
        os.makedirs("graphdata")

    networkhops = traceroute(redis_conn.get('traceTargetHost'))[3]
    redis_conn.set('networkhops', json.dumps(networkhops))

    redis_conn.set('isspeedtestrunning', 'no')
    redis_conn.set('isnetconfigjobrunning', 'no')
    redis_conn.set('currentstate', 'online')
    redis_conn.set('graphdatafolder', str(pathlib.Path.cwd() / "graphdata"))
    redis_conn.set('eventsdatafolder', str(pathlib.Path.cwd() / "events"))
    redis_conn.set('logsdatafolder', str(pathlib.Path.cwd() / "logs"))
    
    redis_conn.set('datetimeformat', get_configValue("datetimeformat"))
    redis_conn.set('defaultinterface', get_configValue("defaultinterface"))
    redis_conn.set('traceTargetHost', get_configValue("tracetargethost"))

@app.context_processor
def get_last_speed_test():
    lastspeedtest = json.loads(redis_conn.get('lastspeedtest'))
    return dict(lastspeedcheck=lastspeedtest)

@app.context_processor
def get_monitor_status():
    if get_configValue("connectionmonitorjobstatus") == "pause":
        status = 'paused'
    else:
        status = redis_conn.get('currentstate')
        
    return dict(monitor_status=status)

@app.context_processor
def get_speedtest_staus():
    if get_configValue("speedtestjobstatus") == "pause":
        status = 'paused'
    else:
        status = redis_conn.get('isspeedtestrunning')
    return dict(speedtest_status=status)

@app.context_processor
def get_netconfig_staus():
    if get_configValue("checknetconfigjobstatus") == "pause":
        status = 'paused'
    else:
        status = redis_conn.get('isnetconfigjobrunning')
    return dict(netconfig_status=status)

@app.context_processor
def lastcheckdate():
    lastcheck = redis_conn.get('lastcheck')
    lastcheck_obj = datetime.strptime(lastcheck, '%Y-%m-%d %H:%M:%S')

    duration = datetime.now() - lastcheck_obj
    lastcheck = humanize.naturaldelta(timedelta(seconds=duration.total_seconds())) + " ago"

    return dict(lastcheckdate=lastcheck)

# ------------------ ROUTES  ------------------ 
app.add_url_rule('/ajax/runspeedtest', view_func=ajax.ajaxspeedtest)
app.add_url_rule('/ajax/listspeedtestservers', view_func=ajax.ajaxListSpeedtestServers)
app.add_url_rule('/ajax/getgraphdata', view_func=ajax.getGraphData)
app.add_url_rule('/ajax/test', view_func=ajax.ajaxTest)

@app.route("/", methods=['GET'])
def home():

    eventsFolder = redis_conn.get('eventsdatafolder')
    logFolder = redis_conn.get('logsdatafolder')
    eventfiles = []
    logfiles = []
    events = []

    for filename in os.listdir(eventsFolder):
        path = os.path.join(eventsFolder, filename)
        if os.path.isfile(path):
            eventfiles.append(filename)

    for filename in os.listdir(logFolder):
        path = os.path.join(logFolder, filename)
        if os.path.isfile(path):
            logfiles.append(filename)

    # Get data from each event
    for file in eventfiles:
        events.append(createEventDict(file))
    
    # Create graphJSON data
    ltgraphJSON = getLatencyGraphData('hour')
    stgraphJSON= getSpeedtestGraphData('week')
    lastSpeedTest = getLastSpeedTest()

    return render_template(
        "home.html",
        events=events,
        isSpeedTestRunning=redis_conn.get('isspeedtestrunning'),
        ltgraphJSON=ltgraphJSON,
        stgraphJSON=stgraphJSON,
        lastSpeedTest=lastSpeedTest,
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
        logger_level = request.form['logginglevel']
        set_configValue('logginglevel', logger_level)
        
        set_configValue("pollfreq", int(request.form['pollfreq']))
        set_configValue('speedtestfreq', int(request.form['speedtestfreq']))
        set_configValue('netconfigtestfreq', int(request.form['netconfigtestfreq']))
        set_configValue('datetimeformat', request.form['datetimeformat'])
        set_configValue('speedtestserverid', request.form['speedtestserverid'])
        set_configValue('defaultinterface', request.form['interfaceRadioGroup'])
        
        set_configValue('connectionmonitorjobstatus', request.form['connectiontestjob_options'])
        set_configValue('speedtestjobstatus', request.form['speedtestjob_options'])
        set_configValue('checknetconfigjobstatus', request.form['netconfigjob_options'])

        if get_configValue("connectionmonitorjobstatus") == "pause":
            jobCheckConnection.pause()
        elif get_configValue("connectionmonitorjobstatus") == "run":
            jobCheckConnection.resume()
        if get_configValue("speedtestjobstatus") == "pause":
            jobSpeedTest.pause()
        elif get_configValue("speedtestjobstatus") == "run":
            jobSpeedTest.resume()
        if get_configValue("checknetconfigjobstatus") == "pause":
            jobCheckNetConfig.pause()
        elif get_configValue("checknetconfigjobstatus") == "run":
            jobCheckNetConfig.resume()

        logger.setLevel(logger_level)
        logger.warning("Logging level set to: " + logger_level)

        hosts = request.form.getlist('hosts')
        host_types = request.form.getlist('hosttype')
        combined_hosts = []

        for host, type in zip(hosts, host_types):
            combined_hosts.append([host, type])

        set_configValue('hosts', combined_hosts)

        return redirect(url_for('home'))

    else:
        interfaces = getLocalInterfaces()

        with open('config.yaml', 'r') as configfile:
            configdict = yaml.safe_load(configfile)

        return render_template("config.html", configdict=configdict, interfaces=interfaces)



if __name__ == "__main__":
    app.run()