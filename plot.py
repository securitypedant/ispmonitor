import plotly.express as px
import json

# Get data
with open('data/' + 'pingResult' + '.json') as file:
    data = {}
    for line in file:
        pair = json.loads(line)
        data.update(pair)

fig = px.line(x=list(data.keys()), y=list(data.values()))
fig.write_html('first_figure.html', auto_open=True)