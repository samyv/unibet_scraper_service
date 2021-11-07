from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
 
 



from app import routes

scheduler = BackgroundScheduler()
scheduler.add_job(func=routes.save_data, trigger="interval", seconds=120)
scheduler.start()

'''
scheduler.add_job(func=routes.delete_data, trigger="interval", seconds=60*60*24)
scheduler.start()
'''

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
