from flask import jsonify, request
from lib.network import runSpeedtest, checkDefaultGateway, checkNetworkHops, checkLocalInterface, checkDNSServers
from lib.datastore import storeMonitorValue
from lib.graphs import getLatencyGraphData, getSpeedtestGraphData
import redis, speedtest, json
import logging, config as config
from lib.redis_server import getRedisConn
from config import get_configValue

logger = logging.getLogger(config.loggerName)

def getGraphData():
    dropdown_value = request.args.get('dropdownValue')
    graph_type = request.args.get('graphType')

    if graph_type == "latency":
        graphData = getLatencyGraphData(dropdown_value)
    else:
         graphData = getSpeedtestGraphData(dropdown_value)

    return graphData

def ajax_checkinterface():
    redis_conn = getRedisConn()
    defaultInterface = redis_conn.get('defaultinterface')
    return checkLocalInterface(defaultInterface)

def ajax_checkdefaultroute():
    return checkDefaultGateway(8)

def ajax_checkdns():
    hosts = get_configValue("hosts")
    return_list = []
    for host in hosts:
        return_list.append(checkDNSServers(host[0]))

    return return_list

def ajax_traceroute():
    redis_conn = getRedisConn()
    networkHops = json.loads(redis_conn.get('networkhops'))
    return checkNetworkHops(networkHops)

def ajaxspeedtest():
    redis_conn = getRedisConn()
    if redis_conn.get('isspeedtestrunning') == "no":
        speedTestResults = runSpeedtest()
        
        intDownloadSpeed = round(speedTestResults.results.download / 1000 / 1000, 1)
        intUploadSpeed = round(speedTestResults.results.upload / 1000 / 1000, 1)

        speedTestResultsList = [intDownloadSpeed, intUploadSpeed]
        storeMonitorValue('speedtestResult', speedTestResultsList)

        speedTestDisplay = "Down=" + str(intDownloadSpeed) + " Mbps, Up=" + str(intUploadSpeed) + " Mbps"
        return jsonify(speedTestDisplay)
    else:
        return jsonify("Speed test already running")

def ajaxListSpeedtestServers():
    logger.debug("Listing speedtest servers")
    servers = []
    serverResult = []

    st = speedtest.Speedtest()
    st_servers = st.get_servers(servers)

    for serverList in st_servers:
            serverResult.append(st_servers[serverList])

    returnResult = jsonify(serverResult)
    
    return returnResult


def ajaxTest():
    redis_conn = getRedisConn()
    networkHopCheck = checkNetworkHops(json.loads(redis_conn.get('networkhops')))

    return jsonify(networkHopCheck)
