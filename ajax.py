from flask import jsonify
from lib.network import runSpeedtest
from lib.datastore import storeMonitorValue
import redis, speedtest
import logging, config as config

logger = logging.getLogger(config.loggerName)

def ajaxspeedtest():
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
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