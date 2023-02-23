from flask import jsonify
from lib.network import runSpeedtest

def runspeedtest():
    speedTestResults = runSpeedtest()
    #speedTestDict = { 'download': speedTestResults.download / 1000 / 1000, 'upload': speedTestResults.upload / 1000 / 1000}
    speedTestDisplay = "Last speed test: Download=" + str(round(speedTestResults.download() / 1000 / 1000,2)) + " MB/s, Upload=" + str(round(speedTestResults.upload() / 1000 / 1000,2)) + " MB/s"
    return jsonify(speedTestDisplay)
