import logging, uuid, config as config
from lib.network import traceroute, runSpeedtest, checkConnection, checkLocalInterface, checkDefaultGateway, checkDNSServers, checkNetworkHops
from config import get_configValue
from lib.datastore import createEvent, updateEvent, storeMonitorValue, getDateNow
from datetime import datetime
from lib.redis_server import getRedisConn

# Setup logging file
logger = logging.getLogger(config.loggerName)

def scheduledCheckNetworkConfig():
    # Examine the current setup of the network and log changes.
    pass

def scheduledSpeedTest():
    redis_conn = getRedisConn()
    if redis_conn.get('isspeedtestrunning') == "no":
        logger.debug("Running speed test")
        speedTestResults = runSpeedtest()
        speedTestResultsList = [round(speedTestResults.results.download / 1000 / 1000, 1), round(speedTestResults.results.upload / 1000 / 1000, 1)]

        storeMonitorValue('speedtestResult', speedTestResultsList)
    else:
        logger.warning("Scheduler attempted to run speedtest job, but it was already running.")

def scheduledCheckConnection():
    redis_conn = getRedisConn()

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
            udpateEvent = {}
            udpateEvent['onlineping'] = speedTest.results.ping
            udpateEvent['downspeed'] = speedTest.results.download
            udpateEvent['upspeed'] = speedTest.results.upload
            udpateEvent['currentState'] = "online"

            # Update event
            updateEvent(redis_conn.get('last_eventid'), udpateEvent)
    else:
        # We are OFFLINE
        # Were we previously offline?
        if redis_conn.get('currentstate') == 'offline':
            # We are STILL OFFLINE
            #event = getEvent(redis_conn.get('last_eventdate') + "-" + redis_conn.get('last_eventid'))
            logger.error("We are still offline:Internet connection down")
        else:
            # We just WENT OFFLINE
            redis_conn.set('currentstate', 'offline')

            # Create a dict to store all the information about the event.
            eventDict = {}
            eventDict['id'] = str(uuid.uuid4())
            eventDict['currentState'] = "offline"
            eventDict['reason'] = 'Unknown'
            eventDict['total_downtime'] = 0
            eventDict['downspeed'] = 0
            eventDict['upspeed'] = 0
            eventDict['onlineping'] = 0
            eventDict['offline_timedate'] = getDateNow()
            eventDict['checks'] = []
            
            # --------------------- LOCAL INTERFACE CHECK ---------------------
            try:
                # Is the local interface working?
                defaultInterface = redis_conn.get('defaultinterface')
                eventDict['checks'].append(checkLocalInterface(defaultInterface))

                if eventDict['checks'][0][2] == False:
                    eventDict['reason'] = "Network interface " + defaultInterface + " not available."
            except Exception as e:
                eventDict['checks'].append(["Exception in local interface check", getDateNow(), False, e.args])

            # --------------------- DEFAULT GATEWAY CHECK ---------------------
            try:
                # Check immediate gateway. Ping default route.
                eventDict['checks'].append(checkDefaultGateway())

                if eventDict['checks'][1][2] == False:
                    eventDict['reason'] = eventDict['checks'][1][3]
            except Exception as e:
                eventDict['checks'].append(["Exception in default gateway check", getDateNow(), False, e.args])

            # --------------------- DNS CHECK ---------------------
            try:
                for host in hosts:
                    eventDict['checks'].append(checkDNSServers(host))
            except Exception as e:
                eventDict['checks'].append(["Exception in DNS check", getDateNow(), False, e.args])

            # --------------------- IMMEDIATE NETWORK HOPS CHECK ---------------------
            try:            
                # Check the hop directly after our gateway. Is it working?
                networkHops = traceroute(redis_conn.get('traceTargetHost'))
                checkNetworkHops(networkHops)
                eventDict['checks'].append()

            except Exception as e:
                eventDict['checks'].append(["Exception in immediate hops check", getDateNow(), False, e.args])

            logger.error("Connection test failed")

            # Store data
            createEvent(eventDict)
            redis_conn.set('last_eventid', eventDict['id'])
            redis_conn.set('last_eventdate', eventDict['offline_timedate'])   
