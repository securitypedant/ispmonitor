from flask import jsonify
from lib.network import runSpeedtest
from lib.datastore import storeMonitorValue
import redis

def apexspeedtest():
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis_conn.get('isspeedtestrunning') == "no":
        speedTestResults = runSpeedtest()
        
        speedTestResultsList = [round(speedTestResults.results.download() / 1000 / 1000, 1), round(speedTestResults.results.upload() / 1000 / 1000, 1)]
        storeMonitorValue('speedtestResult', speedTestResultsList)

        speedTestDisplay = "Last speed test: Download=" + str(round(speedTestResults.download() / 1000 / 1000,2)) + " MB/s, Upload=" + str(round(speedTestResults.upload() / 1000 / 1000,2)) + " MB/s"
        return jsonify(speedTestDisplay)
    else:
        return jsonify("Speed test already running")