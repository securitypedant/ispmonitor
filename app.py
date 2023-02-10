import re
from datetime import datetime

from flask import Flask
from flask import render_template
import json

app = Flask(__name__)


@app.route("/")
def home(status = None):
    return render_template(
        "home.html",
        status="Online",
        date=datetime.now()
    )

@app.route("/api/data")
def get_data():
    with open('data/2023-02-09-6c4ec0af-4e0b-4c89-a17d-f520b52e3ec4', 'r') as file:
            # Reading from json file
            event = file.read()
            #event = json.load(json_file)
    return event