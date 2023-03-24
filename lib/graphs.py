import json, plotly
import plotly.express as px
import pandas as pd
from lib.datastore import readMonitorValues 
from lib.redis_server import getRedisConn
from datetime import datetime, timedelta

redis_conn = getRedisConn()

def getLatencyGraphData(timeFrame):
    graphData = getGraphData(timeFrame, 'pingResult', "", "Latency in ms", "Hosts: ")

    return graphData

def getSpeedtestGraphData(timeFrame):
    graphData = getGraphData(timeFrame, 'speedtestResult', "", "Speed in Mbps", "Bandwidth: ")

    return graphData

def setRangeFromTimeframe(timeFrame):
    # Accept a timeframe as a keyword, then convert to a list of start and end times.
    # Range is [start_date, end_date]
    # In the format, ["2023-03-01 00:00:00", "2023-03-01 23:59:59"]

    listRange = []

    if timeFrame == 'hour':
        today = datetime.now() - timedelta(hours=1)
        listRange.append(datetime.now().strftime(redis_conn.get('datetimeformat')))
        listRange.append(today.strftime(redis_conn.get('datetimeformat')))
    elif timeFrame == 'day':
        today = datetime.now()
        listRange.append(today.strftime(redis_conn.get('datetimeformat')))
        listRange.append(str(today.date())+ " 00:00:00")
    elif timeFrame == 'week':
        today = datetime.now() - timedelta(days=7)
        listRange.append(datetime.now().strftime(redis_conn.get('datetimeformat')))
        listRange.append(str(today.date())+ " 00:00:00")
    elif timeFrame == 'month':
        today = datetime.now() - timedelta(weeks=4)
        listRange.append(datetime.now().strftime(redis_conn.get('datetimeformat')))
        listRange.append(str(today.date()   )+ " 00:00:00")
    else:
        pass

    return listRange

def getGraphData(timeFrame, type, title, yaxis_title, legend_title):
    graphData = readMonitorValues(type, timeFrame)

    if graphData:
        xRef = ""

        timeRange = setRangeFromTimeframe(timeFrame)

        newgraphData = {}
        newgraphData['datetime'] = []

        if type == 'pingResult':
            xRef = "datetime"

            for item in graphData:
                newgraphData['datetime'].append(item['date'])
                data = item['data']
                for latency in data:
                    if latency[0] not in newgraphData:
                        newgraphData[latency[0]] = []
                    newgraphData[latency[0]].append(latency[1])

            dataFrame = pd.DataFrame(newgraphData)

            hostsList = []
            for key, value in newgraphData.items():
                if key != 'datetime':
                    hostsList.append(key)
            yRange = hostsList
        else:
            yRange = ['Download','Upload']
            xRef = 'datetime'

            stxVals = []
            stDownyVals = []
            stUpyVals = []

            for speedTestDict in graphData:
                stxVals.append(speedTestDict['date'])
                stDownyVals.append(int(speedTestDict['data'][0]))
                stUpyVals.append(int(speedTestDict['data'][1]))

            dataFrame = pd.DataFrame({'datetime':stxVals,'Download':stDownyVals,'Upload':stUpyVals})

        fig = px.line(dataFrame, x=xRef, y=yRange, title=title, range_x=timeRange)

        fig.update_layout(
            title=title,
            yaxis_title=yaxis_title,
            xaxis_title="Date / Time",
            legend=dict(x=0, y=1.15, orientation='h'),        
            legend_title=legend_title
        )

        # Create graphJSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        graphJSON = {0:0}
    return graphJSON


