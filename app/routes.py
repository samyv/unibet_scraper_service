from app import app
from driver import UnibetDriver
from app import models
from flask import jsonify

UnibetDriver.open_page()

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route("/getData")
def save_data(): 
    print("[INFO]:\tsaving data...")
    events = UnibetDriver.getEventsData()
    for event in events:
        try:
            event.save_event()
        except Exception as e:
            print(e)
    #TODO: how to return events?
    print("[INFO]:\tsaving data succeeded")
    return jsonify(status = "succeeded")


@app.route("/deleteData")
def delete_data(): 
    print("[INFO]:\tdeleting data...")
    models.Event.query.delete()
    models.EventWinner.query.delete()
    models.OverUnder.query.delete()
    models.db.session.commit()
    print("[INFO]:\tdeleting data succeeded")
    return jsonify(status = "succeeded")