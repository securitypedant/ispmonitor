import plotly.express as px
from lib.datastore import readMonitorValues
from datetime import datetime, date

latencyData = readMonitorValues('pingResult')

xVals = []
yVals = []

for latencyDict in latencyData:
    key = list(latencyDict.keys())
    value = list(latencyDict.values())
    xVals.append(key[0])
    yVals.append(int(value[0]))

fig = px.line(x=xVals, y=yVals, title="Connection latency")
print(fig)
fig.show()