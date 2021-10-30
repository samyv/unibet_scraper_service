from flask import Flask
from flask import jsonify
from flask import make_response #import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
import time
import pandas as pd
import datetime
import pickle
import logging
from json import JSONEncoder

from flask import json
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

class EventEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
app = Flask(__name__)
app.json_encoder = EventEncoder

##PATHS
LEAGUE_AMOUNT = 5
CHROMEDRIVER_PATH = r"chromedriver.exe"
os.environ['PATH'] += CHROMEDRIVER_PATH
UNITBET_PATH_F = r"resources/sport_paths.json"
XPATH_COOKIEBANNER = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
LEAGUES_CLASSNAME = '_086a2'
EVENTS_CLASSNAME = '_0dfcf'
SUBLEAGUES_CLASS_NAME = '_086a2'
TEAMS_CLASS_NAME = 'fe78a'
ODD_CLASS_NAME = 'c93b8'
XPATH_LIST_ALL_LEAGUES = '//*[@id="rightPanel"]/div[3]/div/div/div/div/div/div/div[2]/div[1]/div/div[5]'
##OPTIONS
HEADLESS_DISPLAY = False

all_events = []
driver = None
class Event:
    threeway_odds = []
    overunder_odds = []
    country = ""
    league = ""
    firstTeam = ""
    lastTeam = ""


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    if HEADLESS_DISPLAY:
        options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=options)

def init_paths():
    return json.load(open(UNITBET_PATH_F))

def delete_cookiebanner():
    #wait for and delete cookie banner
    try:
        accept = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, XPATH_COOKIEBANNER)))
        time.sleep(0.5)
        accept.click()
        print_info("cookiebanner deleted")

    except Exception as e:
        print_error("COOKIE BANNER NOT DELETED/FOUND")
        print(e)

def print_info(text):
    print("[INFO] " + text)

def print_error(text):
    print("[ERROR] " + text)

def get_all_leagues_data():
    list_div = driver.find_element_by_xpath(XPATH_LIST_ALL_LEAGUES)
    leagues = WebDriverWait(list_div,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, LEAGUES_CLASSNAME)))
    for i,league in enumerate(leagues[:LEAGUE_AMOUNT]):
        try:
            open_league(league,button=league.find_elements(By.XPATH,".//*")[0])
            subleagues = league.find_elements(By.CLASS_NAME,SUBLEAGUES_CLASS_NAME)
            for subleague in subleagues[1:]:
                open_league(subleague,button=subleague)
        except Exception as e: 
            print(e)
        try: 
            get_events_data(league)
        except Exception as e:
            print(e)
    print_info("all leagues shown")

def open_league(league,button):
    old_len = len(league.text)
    button.click()
    if(old_len > len(league.text)):
        button.click()

def get_events_data(league):
    country = league.text.split("\n")[0]
    try:
        selenium_events = WebDriverWait(league,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, EVENTS_CLASSNAME)))
        for index,selenium_event in enumerate(selenium_events):
            event = ConvertSeleniumEventToEvent(selenium_event,country)
            all_events.append(event)
    except Exception as e:
        print(e)
    return

def ConvertSeleniumEventToEvent(selenium_event,country):
    event =  Event()
    teams = get_teams(selenium_event)
    event.firstTeam = teams[0]
    event.lastTeam = teams[1]
    event.country = country
    leagueText = driver.find_element(locate_with(By.CLASS_NAME, "_78e25").above(selenium_event)).text
    odds = get_event_odds(selenium_event)
    event.three_way_odds = odds[0]
    event.overunder_odds = odds[1]
    event.league = leagueText
    date_event_text = driver.find_element(locate_with(By.TAG_NAME, "time").above(selenium_event)).text.split("\n")[0]
    if("Vandaag" in date_event_text):
        event.timestamp = datetime.date.today().strftime("%d/%m/%Y")
    else:
        event.timestamp = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m/%Y")

    return event

def get_teams(event):
    teams = event.find_elements(By.CLASS_NAME,TEAMS_CLASS_NAME)
    return teams[0].text.replace('\r\n', '-').replace('\n', '-').split("-")

def get_event_odds(event):
    odds = event.find_elements(By.CLASS_NAME,ODD_CLASS_NAME)
    #if(len(odds < 2)):
    #    games.pop()
    three_way_odds = odds[0].text.split('\n')
    over_under_odds = odds[1].text.split('\n')
    return [three_way_odds, over_under_odds]

def convert_events_to_json():
    jsonArray = []
    for event in all_events:
        jsonArray.append((event.__dict__))
    return jsonArray

def get_data():
    print_info("init driver..")
    global driver 
    driver = init_driver()
    driver.maximize_window()
    print_info("driver initialized")

    UNIBET_PATHS = init_paths()
    driver.get(UNIBET_PATHS["football"])

    print_info("deleting delete_cookiebanner")
    delete_cookiebanner()

    print_info("get all leagues")
    get_all_leagues_data()


    print_info("convert events to json")

    events_inJson = convert_events_to_json()

    print_info("done!")
    driver.quit()
    return all_events

@app.route("/")
def home():
    return jsonify(status="UP")

@app.route("/hello/<name>")
def hello_there(name):
    return name

@app.route("/getData")
def return_data():
    global all_events
    events = get_data()
    print(events)
    return make_response(jsonify(events = events))
