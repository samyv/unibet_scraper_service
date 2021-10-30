from flask import Flask

#import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import pickle
import logging
import json
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

##PATHS

CHROMEDRIVER_PATH = r"chromedriver.exe"
os.environ["PATH"] += CHROMEDRIVER_PATH

UNITBET_PATH_F = r"resources/sport_paths.json"
XPATH_COOKIEBANNER = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
LEAGUES_CLASSNAME = '_086a2'
EVENTS_CLASSNAME = '_0dfcf'
SUBLEAGUES_CLASS_NAME = '_086a2'
TEAMS_CLASS_NAME = 'fe78a'
XPATH_LIST_ALL_LEAGUES = '//*[@id="rightPanel"]/div[3]/div/div/div/div/div/div/div[2]/div[1]/div/div[5]'
##OPTIONS
HEADLESS_DISPLAY = False

def init_driver():
    options = Options()
    options.headless = HEADLESS_DISPLAY
    return webdriver.Chrome(options = options)

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

def show_all_leagues():
    list_div = driver.find_element_by_xpath(XPATH_LIST_ALL_LEAGUES)
    leagues = WebDriverWait(list_div,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, LEAGUES_CLASSNAME)))
    for i,league in enumerate(leagues[0:4]):
       button = league.find_elements_by_xpath(".//*")[0]
       button.click()
       subleagues = league.find_elements_by_class_name(SUBLEAGUES_CLASS_NAME)
       for subleague in subleagues[1:]:
           subleague.click()

       # button = league.find_elements_by_xpath(".//*")[0]
        
        #try:
        #    button.click() 
        #    
        #    for subleague in subleagues:
        #        if (len(subleague.text) < 50):
        #            button = subleague.find_elements_by_xpath(".//*")[0]
        #            button.click()
        #            
        #    
        #except Exception as e:
        #    print(e)
    print_info("all leagues shown")

def get_all_events():
    try:
        events = WebDriverWait(driver,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, EVENTS_CLASSNAME)))
        print_info("amount of games: " + str(len(events)))
        for index,event in enumerate(events):
            print_info("event number: " + str(index))
            teams = WebDriverWait(event,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,TEAMS_CLASS_NAME)))
            games.append(teams[0].text)
            print("game: ",teams[0].text.replace('\r\n', ' - ').replace('\n', ' - '))
            print()
            # odds = WebDriverWait(event,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'c93b8')))
            odds = event.find_elements_by_class_name('c93b8')
            if(not(len(odds) > 1 )):
                print("no 1x2")
                x12.append("/")
                over_under.append("/")
                continue
            div_3w = odds[0]
            

            
            way3 = WebDriverWait(div_3w,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_2fe2a')))
            odd = ""
            for res in way3:
                if(res.text):
                    odd += res.text + " "
                else:
                    odd += "/ "
            odd = odd[:-1]
            x12.append(odd)


            if(not(len(odds) > 1 )):
                print("no over under")
                over_under.append("/")
                continue
            div_ou = odds[1]
            ou_odd = WebDriverWait(div_ou,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_2fe2a')))
            overunder = ""
            for i,odd in enumerate(ou_odd):
                if i == 0:
                    span = WebDriverWait(odd,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_139cc')))
                    overunder += span[0].text + " "
                odd_number = WebDriverWait(odd,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_1a584')))
                overunder += odd_number[0].text + " "
            overunder = overunder[:-1]
            over_under.append(overunder)   
    except Exception as e:
        print(e)
    
    
    #7 #unlimited columns
    pd.set_option('display.max_rows', 5000)
    pd.set_option('display.max_columns', 5000)
    pd.set_option('display.width', 1000)

    #Storing lists within dictionary
    dict_gambling = {'Games': games,'Over/Under': over_under, '3-way': x12}
    #Presenting data in dataframe
    df_unibet = pd.DataFrame.from_dict(dict_gambling)
    df_unibet.to_csv("df_unibet.csv")
    #clean leading and trailing whitespaces of all odds
    df_unibet = df_unibet.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    
    print(df_unibet)

    print("done")

print_info("init driver..")
driver = init_driver()
driver.maximize_window()
print_info("driver initialized")

UNIBET_PATHS = init_paths()
driver.get(UNIBET_PATHS["football"])

print_info("deleting delete_cookiebanner")
delete_cookiebanner()

print_info("showing all leagues")
show_all_leagues()
#Initialize your storage
games = []
x12 = []
btts = []
over_under = []
odds_events = []

print_info("get all events")
get_all_events()

#Initialize your storage
games = []
x12 = []
btts = []
over_under = []
odds_events = []



@app.route("/")
def home():
    return "{'status': 'UP'}"

@app.route("/hello/<name>")
def hello_there(name):
    return name


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=print_date_time, trigger="interval", seconds=5)
# scheduler.start()
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())