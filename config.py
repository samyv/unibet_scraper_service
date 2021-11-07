import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:AnubisHeidi5@localhost/england_odds'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HEADLESS_DISPLAY = False
    CHROMEDRIVER_PATH = r"chromedriver.exe"
    UNITBET_PATHS_F = r"resources/links.json"
    
    XPATH_COOKIEBANNER = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
    XPATH_LIST_ALL_LEAGUES = "//*[@id='rightPanel']/div[3]/div/div/div/div/div/div/div[2]/div[1]/div/div[4]"
    
    LEAGUES_CLASSNAME = '_086a2'
    SUBLEAGUES_CLASS_NAME = '_086a2'
    EVENTS_CLASSNAME = '_0dfcf'
    EVENT_ODDS_CLASS_NAME = "_3c5a9"
    ODD_CLASS_NAME = 'c93b8'
    TEAMS_CLASS_NAME = 'fe78a'
    ODD_TYPE_CLASS_NAME = "e517e"
    TIMESTAMP_CLASS_NAME ="e8bfc"
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'flask'
    COUNTRY = "England"
    LEAGUE_AMOUNT = -1