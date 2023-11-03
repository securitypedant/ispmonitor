import logging, uuid, lib.config as config, json
from lib.network import traceroute, run_osSpeedtest, checkConnection, checkLocalInterface, checkDefaultGateway, checkDNSServers, checkNetworkHops
from lib.config import get_file_config_value
from lib.datastore import createEvent, updateEvent, storeMonitorValue, getDateNow, appendEvent
from datetime import datetime
from lib.redis_server import getRedisConn

# Setup logging file
logger = logging.getLogger(config.loggerName)

def scheduledCheckNetworkConfig():
    """ Examine the current setup of the network and log changes. """
    redis_conn = getRedisConn()
    redis_conn.set('isnetconfigjobrunning', 'yes')

    try:
        # Get a list of hosts from a traceroute.
        networkHopsNow = traceroute(redis_conn.get('traceTargetHost'))[3]
        networkHopsPast = json.loads(redis_conn.get('networkhops'))
        
        # Examine the first 5 hops and see if they have changed since the last check.
        for index, host in enumerate(networkHopsNow):
            if host == networkHopsPast[index]:
                # No change to hop
                pass
            else:
                # Hop has changed.
                logger.warning("Network hop to internet has changed. Host:" + host + " and was #" + str(index) + " in the route.")
    except Exception as inst:
        logger.error("Error in network config check: Network hops = " + str(networkHopsNow) + "Exception:" + str(inst))

    redis_conn.set('networkhops', json.dumps(networkHopsNow))
    redis_conn.set('isnetconfigjobrunning', 'no')

def scheduledSpeedTest():
    redis_conn = getRedisConn()
    if redis_conn.get('isspeedtestrunning') == "no" and redis_conn.get('currentState') == 'online':
        logger.info("Running speed test")
        try:
            speedTestResults = run_osSpeedtest()
            speedTestResultsList = [round(speedTestResults['download']['bytes'] / 1000 / 1000, 1), round(speedTestResults['upload']['bytes'] / 1000 / 1000, 1)]
            storeMonitorValue('speedtestResult', speedTestResultsList)
        except Exception as inst:
            logger.error("Speedtest failed in  job: " + inst)    
    else:
        logger.warning("Scheduler attempted to run speedtest job, but it was already running.")

def scheduledCheckConnection():
    redis_conn = getRedisConn()
    if redis_conn.get('isnetconfigjobrunning') == "no" and redis_conn.get('isspeedtestrunning') == "no":

        hosts = get_file_config_value("hosts")
        pollamount = get_file_config_value("pollamount")
        logger.debug("Attempting to reach " + str(hosts))
        redis_conn.set('lastcheck', datetime.now().strftime(get_file_config_value('datetimeformat')))

        # Check connection.
        checkResult = checkConnection(hosts, pollamount)
        
        if checkResult[0] == 'success' or checkResult[0] == 'partial':
            # We are ONLINE
            logger.info("Connection test " + checkResult[0] + " : Pinged hosts " + str(hosts))
            storeMonitorValue('pingResult', checkResult[1])

            # Did we just come back online since previous check?
            if redis_conn.get('currentstate') == 'offline':
                logger.debug("Internet has reconnected.")

                # Set currentstate to online
                redis_conn.set('currentstate', 'online')
                
                # Run speedtest
                speedTest = run_osSpeedtest()
                updateEventDict = {}
                updateEventDict['onlineping'] = speedTest['ping']['latency']
                updateEventDict['downspeed'] = speedTest['download']['bytes']
                updateEventDict['upspeed'] = speedTest['upload']['bytes']
                updateEventDict['currentState'] = "online"
                updateEventDict['online_timedate'] = getDateNow()
                
                # Update event
                updateEvent(redis_conn.get('last_eventid'), updateEventDict)
        else:
            # We are OFFLINE
            # Were we previously offline?
            if redis_conn.get('currentstate') == 'offline':
                # We are STILL OFFLINE
                # event = getEvent(redis_conn.get('last_eventdate') + "-" + redis_conn.get('last_eventid'))
                logger.error("Connection is still offline: Internet connection down")
                checkResult = checkConnection(hosts)
                if checkResult[0] == 'success' or checkResult[0] == 'partial':
                    result = True
                else:
                    result = False

                appendEvent(redis_conn.get('last_eventid'), "Host check during event", getDateNow(), result, checkResult[1])
            else:
                # We just WENT OFFLINE
                logger.error("Connection just went offline")
                redis_conn.set('currentstate', 'offline')

                # Create a dict to store all the information about the event.
                eventDict = {}
                eventDict['id'] = str(uuid.uuid4())
                eventDict['currentState'] = 'offline'
                eventDict['reason'] = 'Unknown'
                eventDict['total_downtime'] = 0
                eventDict['downspeed'] = 0
                eventDict['upspeed'] = 0
                eventDict['onlineping'] = 0
                eventDict['offline_timedate'] = getDateNow()
                eventDict['checks'] = []
                eventDict['notes'] = ''
                
                # --------------------- STORE HOSTS USED FOR CONNECTION ---------------------
                eventDict['checks'].append(["Host check/s failed", getDateNow(), False, checkResult[1]])

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
                        eventDict['checks'].append(checkDNSServers(host[0]))
                        if eventDict['checks'][1][2] == False:
                            eventDict['reason'] = eventDict['checks'][1][3]
                except Exception as e:
                    eventDict['checks'].append(["Exception in DNS check", getDateNow(), False, e.args])

                # --------------------- IMMEDIATE NETWORK HOPS CHECK ---------------------
                try:            
                    # Check the hop directly after our gateway. Is it working?
                    networkHops = json.loads(redis_conn.get('networkhops'))
                    eventDict['checks'].append(checkNetworkHops(networkHops))

                except Exception as e:
                    eventDict['checks'].append(["Exception in network hops check", getDateNow(), False, e.args])

                logger.error("Connection test failed")

                # --------------------- CREATE EVENT ---------------------
                createEvent(eventDict)
                redis_conn.set('last_eventid', eventDict['id'])
                redis_conn.set('last_eventdate', eventDict['offline_timedate'])   
