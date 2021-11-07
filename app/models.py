from os import times
from main import app
from app import db

from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.common.by import By

import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(50))
    league = db.Column(db.String(50))
    home_team = db.Column(db.String(50))
    away_team = db.Column(db.String(50))

    
    def save_event(self):
        db.session.add(self)
        db.session.commit()
    
    def __init__(self,country, league, home_team, away_team):
        self.country = country
        self.league = league
        self.home_team = home_team
        self.away_team =  away_team

class EventWinner(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    home_team_odd = db.Column(db.Float)
    away_team_odd = db.Column(db.Float)
    draw_odd = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    
    def __init__(self, home_team_odd, away_team_odd, draw_odd, event_id):
        self.home_team_odd = home_team_odd if(home_team_odd != "") else None 
        self.away_team_odd = away_team_odd if(away_team_odd != "") else None 
        self.draw_odd = draw_odd if(draw_odd != "") else None 
        self.event_id = event_id

    def save_event_winner(self):
        db.session.add(self)
        db.session.commit()
    

class OverUnder(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    over_under_th = db.Column(db.Float)
    over_under_under_odd = db.Column(db.Float)
    over_under_over_odd = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    def __init__(self, over_under_th, over_under_under_odd, over_under_over_odd, event_id):
        self.over_under_th = over_under_th if(over_under_th != "") else None 
        self.over_under_under_odd = over_under_under_odd if(over_under_under_odd != "") else None 
        self.over_under_over_odd = over_under_over_odd if(over_under_over_odd != "") else None 
        self.event_id = event_id

    def save_over_under_odd(self):
        db.session.add(self)
        db.session.commit()

db.create_all()


class EventConverter:

    @staticmethod
    def get_type_odds(timestamp_block):
        return


    @staticmethod
    def get_event_odds_main(event,type_odds):
        oddbar = event.find_element(By.CLASS_NAME,app.config["EVENT_ODDS_CLASS_NAME"])
        divs_in_oddbar = oddbar.find_elements(By.XPATH, "./*")
        odd_index = 0
        three_way_odds = None
        over_under_odds = None
        for index, div_in_oddbar in enumerate(divs_in_oddbar):
            if(not div_in_oddbar.text):
                continue
            if(index == 1):
                _odd = div_in_oddbar.find_elements(By.CLASS_NAME,"_2fe2a")
                if(len(_odd)== 3 and "c93b8" in div_in_oddbar.get_attribute("class")):
                    three_way_odds = [odd.text for odd in _odd]
                    #TODO what if 3w is less than 3? --> find out which odds
            elif(index == 2):
                _odd = div_in_oddbar.find_elements(By.CLASS_NAME,"_2fe2a")
                if("c93b8" in div_in_oddbar.get_attribute("class")):
                    over_under_odds = [odd.text.replace("\n"," ").split(" ") for odd in _odd]
                    over_under_odds = [item for sublist in over_under_odds for item in sublist]
                
        return [three_way_odds, over_under_odds]

    @staticmethod
    def get_teams(event):
        teams = event.find_elements(By.CLASS_NAME,app.config["TEAMS_CLASS_NAME"])
        return teams[0].text.split("\n")
    
    @staticmethod
    def ConvertSeleniumEventToEvent(selenium_event,selenium_driver,league_name):
        teams = EventConverter.get_teams(selenium_event)
        home_team = teams[0]
        away_team = teams[1]
        country = app.config["COUNTRY"]
        
        #TODO: find date using timestamp block
        date_element =  " ".join(selenium_driver.find_element(locate_with(By.TAG_NAME, "time").above(selenium_event)).get_attribute("datetime").split(" ")[0:4])
        date_event = datetime.datetime.strptime(date_element, '%a %b %d %Y')
        timestamp = date_event
        
        event = Event(country = country, league = league_name, home_team = home_team, away_team = away_team)
        return event

    @staticmethod
    def save_event_result_odd(threeway_odds,event_id):
        home_team_odd, draw_odd, away_team_odd= threeway_odds
        event_winner_odds = EventWinner(home_team_odd=home_team_odd, away_team_odd=away_team_odd, draw_odd=draw_odd,event_id=event_id)
        event_winner_odds.save_event_winner()
        return

    @staticmethod
    def save_over_under_odd(over_under_odds,event_id):
        over_under_th,over_under_over_odd  , _, over_under_under_odd = over_under_odds
        over_under_odd = OverUnder(over_under_th = over_under_th,over_under_over_odd = over_under_over_odd, over_under_under_odd = over_under_under_odd, event_id = event_id)
        over_under_odd.save_over_under_odd()
        return 


    @staticmethod
    def save_odds(selenium_event,type_odds,event_id):
        #TODO: use type_odds

        odds = EventConverter.get_event_odds_main(selenium_event,type_odds)
        if(odds[0] != None):
            EventConverter.save_event_result_odd(odds[0],event_id)
            
        if(odds[1] != None):
            EventConverter.save_over_under_odd(odds[1],event_id)

    
    
    @staticmethod
    def jsonifyEvents(events):
        return