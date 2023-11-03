import json, os, pathlib, yaml, humanize, logging, ajax

import logging.handlers as handlers
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, render_template, request, url_for, g

from lib.config import get_file_config_value, set_file_config_value, DATE_FORMAT, update_config, read_config
from jobs import (scheduledCheckConnection, scheduledCheckNetworkConfig,
                  scheduledSpeedTest)
from lib.datastore import (db_connect, db_close, createEventDict, deleteEvent, getLastSpeedTest,
                           updateEvent, set_db_config_value, get_db_config_value)

from lib.datastore import DBConnection
from lib.graphs import getLatencyGraphData, getSpeedtestGraphData
from lib.network import getLocalInterfaces, traceroute

app = Flask(__name__)
# Details on the Secret Key: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
# NOTE: The secret key is used to cryptographically-sign the cookies used for storing the session data.
app.secret_key = get_file_config_value("appSecretKey")

# Constants
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CONFIG_FILE = "config/config.yaml"

# Setup database config.
setup_config()

# FIXME: Poor hack for folder creation on startup. Move this to a check environment function.
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data/logs"):
    os.makedirs("data/logs")

# Setup logging file
logger = logging.getLogger(config.loggerName)

####### SETUP SCHEDULER #######
# FIXME: Can we do all this in another file? Keep this app file as clean as we can?
ap_logger = logging.getLogger('apscheduler')

aplog_file_handler = logging.FileHandler('data/logs/apscheduler.log')
aplog_file_handler.setLevel(get_file_config_value("logginglevel"))

ap_logger.setLevel(get_file_config_value("logginglevel"))
ap_logger.addHandler(aplog_file_handler)

scheduler = BackgroundScheduler(logger=ap_logger)
scheduler.start()

jobCheckConnection = scheduler.add_job(scheduledCheckConnection, 'interval', seconds=get_file_config_value("pollfreq"), max_instances=1)
jobSpeedTest = scheduler.add_job(scheduledSpeedTest, 'interval', seconds=get_file_config_value("speedtestfreq"), max_instances=1)
jobCheckNetConfig = scheduler.add_job(scheduledCheckNetworkConfig, 'interval', seconds=get_file_config_value("netconfigtestfreq"), max_instances=1)

if get_file_config_value("connectionmonitorjobstatus") == "pause":
    jobCheckConnection.pause()
if get_file_config_value("speedtestjobstatus") == "pause":
    jobSpeedTest.pause()
if get_file_config_value("checknetconfigjobstatus") == "pause":
    jobCheckNetConfig.pause()

update_config("jobIDCheckConnection", jobCheckConnection.id)
update_config("jobIDSpeedTest", jobSpeedTest.id)
update_config("jobIDCheckNetConfig", jobCheckNetConfig.id)

@app.before_first_request
def appStartup():
    
    # Check if required folders exist.
    # FIXME: Must be a much better way of handling this.
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists("data/logs"):
        os.makedirs("data/logs")

    if not os.path.exists("data/events"):
        os.makedirs("data/events")

    if not os.path.exists("data/graphdata"):
        os.makedirs("data/graphdata")

    # This database connection should now last forever.
    db = db_connect(DBConnection(mongodb_host, mongodb_port, mongodb_user, mongodb_pass), mongodb_name, True)


    update_config("currentState", "online")
    update_config("isspeedtestrunning", "no")
    update_config("isnetconfigjobrunning", "no")
    update_config("lastcheck", datetime.now().strftime(get_file_config_value('datetimeformat')))
    update_config("graphdatafolder", str(pathlib.Path.cwd() / "data/graphdata"))
    update_config("eventsdatafolder", str(pathlib.Path.cwd() / "data/events"))
    update_config("logsdatafolder", str(pathlib.Path.cwd() / "data/logs"))
    update_config("datetimeformat", DATE_FORMAT)
    update_config("defaultinterface", get_file_config_value("defaultinterface"))
    update_config("lastspeedtest", json.dumps({"ping":"0", "download": "0", "upload": "0", "server":"None"}))    
    update_config("traceTargetHost", get_file_config_value("tracetargethost"))
    
    networkhops = traceroute(read_config("traceTargetHost"))[3]
    update_config("networkhops", json.dumps(networkhops))

    logger.setLevel(get_file_config_value("logginglevel"))
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    logHandler = handlers.TimedRotatingFileHandler(read_config("logsdatafolder") + '/monitor.log', when='D', interval=1, backupCount=7)
    logHandler.setLevel(get_file_config_value("logginglevel"))
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

@app.context_processor
def get_last_speed_test():
    lastspeedtest = json.loads(get_db_config_value(g.db, "lastspeedtest"))
    return dict(lastspeedcheck=lastspeedtest)

@app.context_processor
def get_monitor_status():
    if get_file_config_value("connectionmonitorjobstatus") == "pause":
        status = 'paused'
    else:
        status = get_db_config_value(g.db, "currentstate")
        
    return dict(monitor_status=status)

@app.context_processor
def get_speedtest_staus():
    if get_file_config_value("speedtestjobstatus") == "pause":
        status = 'paused'
    else:
        status = get_db_config_value(g.db, "isspeedtestrunning")
    return dict(speedtest_status=status)

@app.context_processor
def get_netconfig_staus():
    if get_file_config_value("checknetconfigjobstatus") == "pause":
        status = 'paused'
    else:
        status = get_db_config_value(g.db, "isnetconfigjobrunning")
    return dict(netconfig_status=status)

@app.context_processor
def lastcheckdate():
    lastcheck = get_db_config_value(g.db, "lastcheck")
    lastcheck_obj = datetime.strptime(lastcheck, '%Y-%m-%d %H:%M:%S')

    duration = datetime.now() - lastcheck_obj
    lastcheck = humanize.naturaldelta(timedelta(seconds=duration.total_seconds())) + " ago"

    return dict(lastcheckdate=lastcheck)

# ------------------ ROUTES  ------------------ 
app.add_url_rule('/ajax/checkinterface', view_func=ajax.ajax_checkinterface)
app.add_url_rule('/ajax/checkdefaultroute', view_func=ajax.ajax_checkdefaultroute)
app.add_url_rule('/ajax/checkdns', view_func=ajax.ajax_checkdns)
app.add_url_rule('/ajax/traceroute', view_func=ajax.ajax_traceroute)

app.add_url_rule('/ajax/runspeedtest', view_func=ajax.ajaxspeedtest)
app.add_url_rule('/ajax/listspeedtestservers', view_func=ajax.ajaxListSpeedtestServers)
app.add_url_rule('/ajax/getgraphdata', view_func=ajax.getGraphData)
app.add_url_rule('/ajax/test', view_func=ajax.ajaxTest)

@app.route("/", methods=['GET'])
def home():

    eventsFolder = get_db_config_value(g.db, "eventsdatafolder")
    logFolder = get_db_config_value(g.db, "logsdatafolder")
    eventfiles = []
    logfiles = []
    events = []

    for filename in os.listdir(eventsFolder):
        path = os.path.join(eventsFolder, filename)
        if os.path.isfile(path):
            eventfiles.append(filename)

    files = os.listdir(logFolder)
    # include only files starting with "monitor"
    filtered_files = [file for file in files if file.startswith('monitor')]

    for file in filtered_files:
        path = os.path.join(logFolder, file)
        if os.path.isfile(path):
            logfiles.append(file)

    sorted_logfilelist = sorted(logfiles, key=lambda x: os.path.getmtime(os.path.join(logFolder, x)), reverse=True)

    # Get data from each event
    for file in eventfiles:
        events.append(createEventDict(file))
    
    sorted_events = sorted(events, key=lambda x: datetime.strptime(x['offline_timedate'], get_file_config_value('datetimeformat')), reverse=True)

    # Create graphJSON data
    ltgraphJSON = getLatencyGraphData('hour')
    stgraphJSON= getSpeedtestGraphData('week')
    lastSpeedTest = getLastSpeedTest()

    return render_template(
        "home.html",
        events=sorted_events,
        isSpeedTestRunning=get_db_config_value(g.db, "isspeedtestrunning"),
        ltgraphJSON=ltgraphJSON,
        stgraphJSON=stgraphJSON,
        lastSpeedTest=lastSpeedTest,
        logfiles=sorted_logfilelist
    )

@app.route("/log")
def log():
    logfile = request.args.get("logid")
    with open('data/logs/' + str(logfile), 'r') as file: 
        lines = file.readlines()
        return render_template("log.html", lines=lines, logfilename=logfile)

@app.route("/event", methods=['GET', 'POST'])
def event():
    if request.method == 'POST':
        if 'save' in request.form:
            # Save title and notes to event and then return home.
            with open(pathlib.Path(get_db_config_value(g.db, "eventsdatafolder")) / request.form['eventid'], 'r') as json_file:
                # Reading from json file
                json_object = json.load(json_file)
                json_object['notes'] = request.form['notes']
                json_object['reason'] = request.form['reason']
                updateEvent(request.form['eventid'], json_object)
        elif 'delete' in request.form:
            # Delete the event record.    
            deleteEvent(request.form['eventid'])
        return redirect(url_for('home'))
    else:
        eventid = request.args.get("eventid")
        eventdict = createEventDict(eventid)
        return render_template("event.html", event=eventdict)

@app.route("/tools", methods=['GET', 'POST'])
def tools():
    return render_template("tools.html")

@app.route("/config", methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        #Enumerate form data into file.
        logger_level = request.form['logginglevel']
        set_file_config_value('logginglevel', logger_level)
        
        set_file_config_value("pollfreq", int(request.form['pollfreq']))
        set_file_config_value("pollamount", int(request.form['pollamount']))
        set_file_config_value('speedtestfreq', int(request.form['speedtestfreq']))
        set_file_config_value('netconfigtestfreq', int(request.form['netconfigtestfreq']))
        set_file_config_value('datetimeformat', request.form['datetimeformat'])
        set_file_config_value('speedtestserverid', request.form['speedtestserverid'])

        set_file_config_value('defaultinterface', request.form['interfaceRadioGroup'])
        redis_conn.set('defaultinterface', request.form['interfaceRadioGroup'])
        
        set_file_config_value('connectionmonitorjobstatus', request.form['connectiontestjob_options'])
        set_file_config_value('speedtestjobstatus', request.form['speedtestjob_options'])
        set_file_config_value('checknetconfigjobstatus', request.form['netconfigjob_options'])

        if get_file_config_value("connectionmonitorjobstatus") == "pause":
            jobCheckConnection.pause()
        elif get_file_config_value("connectionmonitorjobstatus") == "run":
            jobCheckConnection.resume()
        if get_file_config_value("speedtestjobstatus") == "pause":
            jobSpeedTest.pause()
        elif get_file_config_value("speedtestjobstatus") == "run":
            jobSpeedTest.resume()
        if get_file_config_value("checknetconfigjobstatus") == "pause":
            jobCheckNetConfig.pause()
        elif get_file_config_value("checknetconfigjobstatus") == "run":
            jobCheckNetConfig.resume()

        logger.setLevel(logger_level)
        logger.warning("Logging level set to: " + logger_level)

        hosts = request.form.getlist('hosts')
        host_types = request.form.getlist('hosttype')
        combined_hosts = []

        for host, type in zip(hosts, host_types):
            combined_hosts.append([host, type])

        set_file_config_value('hosts', combined_hosts)

        return redirect(url_for('home'))

    else:
        interfaces = getLocalInterfaces()

        with open('config/config.yaml', 'r') as configfile:
            configdict = yaml.safe_load(configfile)

        return render_template("config.html", configdict=configdict, interfaces=interfaces)



if __name__ == "__main__":
    app.run()