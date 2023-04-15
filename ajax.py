import json
import logging
import subprocess

from flask import jsonify, request

import config as config
from config import get_configValue
from lib.datastore import storeMonitorValue
from lib.graphs import getLatencyGraphData, getSpeedtestGraphData
from lib.network import (checkDefaultGateway, checkDNSServers,
                         checkLocalInterface, checkNetworkHops,
                         run_osSpeedtest)
from lib.redis_server import getRedisConn

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
    if redis_conn.get('isspeedtestrunning') == "no" and redis_conn.get('currentState') == 'online':
        try:
            speedTestResults = run_osSpeedtest()
            
            intDownloadSpeed = round(speedTestResults['download']['bytes'] / 1000 / 1000, 1)
            intUploadSpeed = round(speedTestResults['upload']['bytes'] / 1000 / 1000, 1)
            speedTestResultsList = [intDownloadSpeed, intUploadSpeed]
            
            storeMonitorValue('speedtestResult', speedTestResultsList)
            speedTestDisplay = "Down=" + str(intDownloadSpeed) + " Mbps, Up=" + str(intUploadSpeed) + " Mbps"
            return jsonify(speedTestDisplay)
        except Exception as inst:
            return jsonify("Speedtest failed: " + inst)
    else:
        return jsonify("Speedtest already running")

def ajaxListSpeedtestServers():
    logger.debug("Listing speedtest servers")
    servers = []
    serverResult = []

    output_bytes = subprocess.check_output(['speedtest', "-L", "--format=json"])
    output_string = json.loads(output_bytes.decode('utf-8'))

    for serverList in output_string['servers']:
            serverResult.append([serverList['id'], serverList['name'], serverList['host']])

    returnResult = jsonify(serverResult)
    
    return returnResult


def ajaxTest():
    redis_conn = getRedisConn()
    networkHopCheck = checkNetworkHops(json.loads(redis_conn.get('networkhops')))

    return jsonify(networkHopCheck)
