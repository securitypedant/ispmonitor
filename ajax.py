from flask import jsonify, request
from lib.network import runSpeedtest, checkDefaultGateway
from lib.datastore import storeMonitorValue
from lib.graphs import getLatencyGraphData
import redis, speedtest
import logging, config as config
from lib.redis_server import getRedisConn

logger = logging.getLogger(config.loggerName)

def getGraphData():
    dropdown_value = request.args.get('dropdownValue')

    updated_data = getLatencyGraphData(dropdown_value)

    return updated_data

def ajaxspeedtest():
    redis_conn = getRedisConn()
    if redis_conn.get('isspeedtestrunning') == "no":
        speedTestResults = runSpeedtest()
        
        intDownloadSpeed = round(speedTestResults.results.download / 1000 / 1000, 1)
        intUploadSpeed = round(speedTestResults.results.upload / 1000 / 1000, 1)

        speedTestResultsList = [intDownloadSpeed, intUploadSpeed]
        storeMonitorValue('speedtestResult', speedTestResultsList)

        speedTestDisplay = "Last speed test: Download=" + str(intDownloadSpeed) + " MB/s, Upload=" + str(intUploadSpeed) + " MB/s"
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
    isLocalInterfaceUp = checkDefaultGateway()

    return jsonify(isLocalInterfaceUp)
