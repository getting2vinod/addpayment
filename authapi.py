from urllib.parse import unquote
from flask import Blueprint, redirect, url_for, request, session, g
import requests
#import sqlite3
import os
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import json
import urllib

config_file = "./auth.config"
config = None

auth = Blueprint('auth', __name__)

db = SQLAlchemy()


basedir = os.path.abspath(os.path.dirname(__file__))
sessionKey = "authapi@#SessionKeeeeey"
tokenName = "auth-x-token"
userName = "auth-x-username"
privateKey = "this@@@ismy$$$superlong!!sessionKeyabcdef"
server_session = None
with open(config_file) as json_file:
    config = json.load(json_file)
    
def init(app):
    app.before_request(check_login)
   
    
    

@auth.record_once
def on_load(state):
    
    """Initialize session management and database for this blueprint."""
    app = state.app
     # Configure SQLAlchemy for the blueprinto    
   
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sessions.db')
    # Attach SQLAlchemy to Flask-Session
    app.config['SECRET_KEY'] = sessionKey
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_COOKIE_NAME'] = 'mypayment'
    db.init_app(app)

    # Create the sessions table if not exists
    with app.app_context():
        db.create_all()
    Session(app)

    
#server_session["test"] = "something"
#KA0319930002932

@auth.route("/sessioncheck")
def sessioncheck():
    s = session.get("myval")
    if s is not None:
        session["myval"] = (int(s)+1)
    else:
        session["myval"] = 0
    return "Session val : " + str(session.get("myval")) + " sessionid :" + str(session.get("sid") or "")




def check_login():
    if(request.path not in config["auth"]["ignoredRoutes"]):
        if config:        
            url = "http://" + config["auth"]["serverurl"]+ ":" + str(config["auth"]["port"]) 
            if session.get(tokenName):
                    resp = requests.get(url+ "/validate/"+session.get(tokenName))
                    rp = resp.json()
                    if rp["success"]:
                        return None
                    else:
                        session["_source"] = urllib.parse.quote(request.url)       
                        signonUrl = url + "/signon?callback=" + urllib.parse.quote(request.base_url + "/callback")
                        #send callback url and _source
                        return redirect(signonUrl)
                
            else: # no token found to sign in
                session["_source"] = urllib.parse.quote(request.url)       
                signonUrl = url + "/signon?callback=" + urllib.parse.quote(request.base_url + "/callback")
                #send callback url and _source
                return redirect(signonUrl)
        else:
            return({'success':False})
    else:
        return None

@auth.route("/logout", methods=['GET'])
def logout():
    session.clear()
    url = "http://" + config["auth"]["serverurl"]+ ":" + str(config["auth"]["port"]) 
    return redirect(url + "/logout")

@auth.route("/callback", methods=['GET'])
def callback():
    #to receive username/token/expires
    singleuse = request.args.get("singleuse")
    url = "http://" + config["auth"]["serverurl"]+ ":" + str(config["auth"]["port"]) 
    if(singleuse):
        #pl = json.loads(payload)
        #use key to get token
        resp = requests.get(url+ "/gettokenfromkey/"+privateKey+"/"+singleuse)
        rp = resp.json()        
        session[tokenName] = rp["token"]        
        return redirect(unquote(session["_source"]))
    else:
        return ("Invalid handshake or user not registered.")




