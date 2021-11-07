import datetime
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.common.by import By
from flask_sqlalchemy import SQLAlchemy
from flask import current_app,g
from flask import Flask
import sqlite3

db = SQLAlchemy(current_app)
class Event(db.Model):
    country = db.Column(db.String(50))
    league = db.Column(db.String(50))
    home_team = db.Column(db.String(50))
    away_team = db.Column(db.String(50))

    over_under_th = db.Column(db.Double)
    over_under_under_odd = db.Column(db.Double)
    over_under_over_odd = db.Column(db.Double)
    home_team_odd = db.Column(db.Double)
    away_team_odd = db.Column(db.Double)
    draw_odd = db.Column(db.Double)

    
    def save_event(self):
        db.session.add(self)
        db.session.commit()
    
    def __init__(self,over_under_th, over_under_under_odd, over_under_over_odd, home_team_odd, away_team_odd, draw_odd, country, league, firstTeam, lastTeam):
        self.country = country
        self.league = league
        self.firstTeam = firstTeam
        self.lastTeam =  lastTeam
        self.over_under_th = over_under_th
        self.over_under_under_odd = over_under_under_odd
        self.over_under_over_odd = over_under_over_odd
        self.home_team_odd = home_team_odd
        self.away_team_odd = away_team_odd
        self.draw_odd = draw_odd

db.create_all()

class EventConverter:
    ODD_CLASS_NAME = 'c93b8'
    TEAMS_CLASS_NAME = 'fe78a'

    @staticmethod
    def get_event_odds(event):
        odds = event.find_elements(By.CLASS_NAME,EventConverter.ODD_CLASS_NAME)
        three_way_odds = None
        over_under_odds = None
        for odd in odds:
            type_odd = odd.find_element(locate_with(By.CLASS_NAME, "_069a3").above(odd)).text
            _odd = odd.find_elements(By.CLASS_NAME,"_2fe2a")
            if("Wedstrijd" in type_odd):
                three_way_odds = _odd.text.split('\n')
            elif("Totaal Aantal Doelpunten" in type_odd):
                over_under_odds = _odd.text.split('\n')
        return [three_way_odds, over_under_odds]

    @staticmethod
    def get_teams(event):
        teams = event.find_elements(By.CLASS_NAME,EventConverter.TEAMS_CLASS_NAME)
        return teams[0].text.replace('\r\n', '-').replace('\n', '-').split("-")
    
    @staticmethod
    def ConvertSeleniumEventToEvent(selenium_event,selenium_driver,league_name):
        event =  Event()
        teams = EventConverter.get_teams(selenium_event)
        firstTeam = teams[0]
        lastTeam = teams[1]
        country = "Belgium"
        odds = EventConverter.get_event_odds(selenium_event)
        if(odds[0] != None):
            event.threeway_odds = odds[0]
        if(odds[1] != None):
            event.overunder_odds = odds[1]
        date_element =  " ".join(selenium_driver.find_element(locate_with(By.TAG_NAME, "time").above(selenium_event)).get_attribute("datetime").split(" ")[0:4])
        date_event = datetime.datetime.strptime(date_element, '%a %b %d %Y')
        date_event_text = date_event.strftime('%d-%m-%Y')
        event.timestamp = date_event_text
      
        return event

    @staticmethod
    def jsonifyEvents(events):
        return