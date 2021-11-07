from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with

import json
import time
from app.models import Event,EventConverter

from main import app

class UnibetDriver:
    __instance = None
    selenium_driver = None
    PAGE_LOADED = False
    leagues = None

    @staticmethod 
    def delete_cookiebanner(webdriver):
        #wait for and delete cookie banner
        try:
            accept = WebDriverWait(webdriver, 15).until(EC.element_to_be_clickable((By.XPATH, app.config["XPATH_COOKIEBANNER"])))
            webdriver.implicitly_wait(10) 
            accept.click()

        except Exception as e:
            print(e)
    
    @staticmethod
    def open_league(league,button):
        old_len = len(league.text)
        button.click()
        if(old_len > len(league.text)):
            button.click()

    @staticmethod 
    def open_all_leagues(webdriver):
        list_div = webdriver.find_element(By.XPATH, app.config["XPATH_LIST_ALL_LEAGUES"])
        leagues = WebDriverWait(list_div,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, app.config["LEAGUES_CLASSNAME"])))
        
        if(app.config["LEAGUE_AMOUNT"] == -1):
            LEAGUE_AMOUNT = len(leagues)
        for i,league in enumerate(leagues[:LEAGUE_AMOUNT]):
            try:
                UnibetDriver.open_league(league,button=league.find_elements(By.XPATH,".//*")[0])
            except Exception as e: 
                print("something went wrong")
            """try: 
                get_events_data(league)
            except Exception as e:
                print("something went wrong")"""
        return leagues
    
    @staticmethod    
    def get_options():
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            if False:
                options.add_argument("--headless")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            return options

    @staticmethod
    def get_type_odds(driver):
        type_selector_text = driver.find_element(By.CLASS_NAME, app.config["ODD_TYPE_CLASS_NAME"]).text[18:].split(" & ")
        return type_selector_text

    @staticmethod
    def get_events_data(webdriver, leagues):
        all_events = []
        for league in leagues:
            league_name = league.text.split("\n")[0]
            selenium_events = WebDriverWait(league,5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, app.config["EVENTS_CLASSNAME"])))
            for selenium_event in selenium_events:
                try:
                    #save_event()
                    #save_odds(event_id)
                    type_odds = UnibetDriver.get_type_odds(webdriver)
                    event = EventConverter.ConvertSeleniumEventToEvent(selenium_event,webdriver,league_name)
                    event.save_event()
                    EventConverter.save_odds(selenium_event,type_odds,event.id)
                    all_events.append(event)
                except Exception as e:
                    print(e)
        return all_events

    @staticmethod 
    def get_instance():
      """ Static access method. """
      if UnibetDriver.__instance == None:
         UnibetDriver()
      return UnibetDriver.__instance
    
    def __init__(self):
        if not UnibetDriver.__instance:
            self.selenium_driver = webdriver.Chrome(r'chromedriver.exe',options=UnibetDriver.get_options())
            UnibetDriver.__instance = self
    
    @staticmethod
    def open_page():
        unibet_dr = UnibetDriver().get_instance()
        UNIBET_PATHS = json.load(open(app.config["UNITBET_PATHS_F"]))
        unibet_dr.selenium_driver.get(UNIBET_PATHS[0])
        UnibetDriver.delete_cookiebanner(unibet_dr.selenium_driver)
        unibet_dr.leagues = UnibetDriver.open_all_leagues(unibet_dr.selenium_driver)
        unibet_dr.PAGE_LOADED = True
        print("PAGE READY")


    @staticmethod   
    def getEventsData():
        driver = UnibetDriver.get_instance()
        if(not driver.PAGE_LOADED): 
            UnibetDriver.open_page()
        events = UnibetDriver.get_events_data(driver.selenium_driver,driver.leagues)
        
        return events
