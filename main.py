import redis, logging, uuid, config as config

from lib.network import traceroute, runSpeedtest, checkConnection, checkLocalInterface, checkDefaultGateway, checkDNSServers
from config import set_configValue, get_configValue
from lib.datastore import createEvent, updateEvent, monitorEvent, getEvent, storeMonitorValue, getDateNow
from datetime import date, datetime

# Constants and config
eventID = ""
eventDate = ""
traceTargetHost = "8.8.8.8"

# Setup logging file
logger = logging.getLogger(config.loggerName)

def scheduledCheckNetworkConfig():
    # Examine the current setup of the network and log changes.
    pass

def scheduledSpeedTest():
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis_conn.get('isspeedtestrunning') == "no":
        logger.debug("Running speed test")
        speedTestResults = runSpeedtest()
        speedTestResultsList = [round(speedTestResults.results.download / 1000 / 1000, 1), round(speedTestResults.results.upload / 1000 / 1000, 1)]

        storeMonitorValue('speedtestResult', speedTestResultsList)
    else:
        logger.warning("Scheduler attempted to run speedtest job, but it was already running.")

def scheduledCheckConnection():
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    hosts = get_configValue("hosts")
    logger.debug("Attempting to reach " + str(hosts))
    redis_conn.set('lastcheck', datetime.now().strftime(get_configValue('datetimeformat')))

    # Check connection.
    checkResult = checkConnection(hosts)
    
    if checkResult[0] == 'Success' or checkResult[0] == 'Partial':
        # We are ONLINE
        logger.info("Connection test " + checkResult[0] + " : Pinged hosts " + str(hosts))
        storeMonitorValue('pingResult', checkResult[1])

        # Did we just come back online since previous check?
        if redis_conn.get('currentstate') == 'offline':
            logger.debug("Internet has reconnected.")

            # Set currentstate to online
            redis_conn.set('currentstate', 'online')
            
            # Run speedtest
            speedTest = runSpeedtest()
            event = monitorEvent(redis_conn.get('eventid'))
            event.onlineping = speedTest.results.ping
            event.downspeed = speedTest.results.download
            event.upspeed = speedTest.results.upload

            # Update event
            updateEvent(str(redis_conn.get('eventdate')) + "-" + redis_conn.get('eventid'), event)
    else:
        # We are OFFLINE
        # Were we previously offline?
        if redis_conn.get('currentstate') == 'offline':
            # We are STILL OFFLINE

            event = getEvent(redis_conn.get('eventdate') + "-" + redis_conn.get('eventid'))
            logger.error("We are still offline:Internet connection down since " + event["offlinetimedate"])
        else:
            # We just WENT OFFLINE
            redis_conn.set('currentstate', 'offline')

            # Create a dict to store all the information about the event.
            eventDict = {}
            eventDict['id'] = str(uuid.uuid4())
            eventDict['currentState'] = "offline"
            eventDict['reason'] = 'Unknown'
            eventDict['offline_timedate'] = getDateNow()
            eventDict['checks'] = []
            
            # Is the local interface working?
            defaultInterface = redis_conn.get('defaultinterface')
            eventDict['checks'].append(checkLocalInterface(defaultInterface))

            # Check immediate gateway. Ping default route.
            eventDict['checks'].append(checkDefaultGateway())

            # Is DNS resolving?
            for host in hosts:
                eventDict['checks'].append(checkDNSServers(host))
             
            # Check the hop directly after our gateway. Is it working?
            eventDict['tracedHosts'] = traceroute(traceTargetHost)

            logger.error("Connection test failed:Traced hosts " + str(eventDict['tracedHosts']))

            # Store data
            createEvent(eventDict)
            redis_conn.set('eventid', eventDict['id'])
            redis_conn.set('eventdate', eventDict['offline_timedate'])   
