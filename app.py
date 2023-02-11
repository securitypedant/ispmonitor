import os
from datetime import datetime
from flask import Flask, render_template, request
from config import set_configValue, get_configValue

app = Flask(__name__)


@app.route("/")
def home():
    folder = "data"
    files = []
    status = get_configValue("currentstate")
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            files.append(filename)

    return render_template(
        "home.html",
        status=status,
        files=files
    )

@app.route("/log")
def log():
    with open("logs/monitor.log") as file: 
        loglines = file.readlines()
        return render_template("log.html", loglines=loglines)

@app.route("/event")
def event():
    eventid = request.args.get("eventid")
    with open('data/' + eventid, 'r') as file:
        return render_template("event.html", file=file)


@app.route("/api/data")
def get_data():
    with open('data/2023-02-09-6c4ec0af-4e0b-4c89-a17d-f520b52e3ec4', 'r') as file:
            # Reading from json file
            event = file.read()
            #event = json.load(json_file)
    return event