from flask import Blueprint, render_template, redirect, url_for, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from googleapiclient.discovery import build
from google.oauth2 import service_account
import hmac
import hashlib
import secrets
import datetime
import sqlite3


ignoreRoutes = [] #the routes defined here would be ignored by auth

AUTH_SHEET_ID = "1ge1ICzCRMXXHbllb9Rl9A90UiVWCXZkgGRuDvIBfgpA"
SCOPES = ""
SERVICE_ACCOUNT_FILE = ""
AUTH_SHEET_RANGE = 'Auth!A2:F'
app = None
creds = None
pwdhashkey = "thisismysuuuuuuperlonghashKey"

auth = Blueprint('auth', __name__)

auth.template_folder = "./"

db_name = "./tokens.db"

def encrypt(txt):
    txt = txt.encode()
    skey = pwdhashkey.encode()
    hmac_object = hmac.new(skey, txt, hashlib.sha256)
    return hmac_object.hexdigest()

def init(scopes, keyJson, ir, app):
    ignoreRoutes.extend(ir)
    SCOPES=scopes
    SERVICE_ACCOUNT_FILE = keyJson   
    app = app
    auth.creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #adding in login and logout to ignore
    ignoreRoutes.append("/login")
    ignoreRoutes.append("/register")
    ignoreRoutes.append("/logout")
    ignoreRoutes.append("/favicon.ico")
    app.before_request(check_login)
    

def upsert_by_name(uname, token):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY,
        uname TEXT UNIQUE,
        token TEXT
    )
    ''')
    cursor.execute('''
    INSERT OR REPLACE INTO tokens (id, uname, token)
    VALUES (
        (SELECT id FROM tokens WHERE uname = ?),
        ?, ?
    )
    ''', (uname, uname, token))
    conn.commit()
    conn.close()

def read_record_by_uname(uname):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tokens WHERE uname = ?', (uname,))
    row = cursor.fetchone()
    conn.close()
    return row


def check_login():
    if(request.path not in ignoreRoutes):
        if session.get("x-token") != None and session.get("x-uname") != None:
            profileRow = read_record_by_uname(session.get("x-uname").tolower())
            
            if session["x-token"] in profileRow[2]:
                return None
            else:
                session["redirect-to"] = request.url
                return render_template('login.html')
        else:
            session["redirect-to"] = request.url
            return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     return None


@auth.route("/login", methods=['POST'])
def login():
    p = request.form.get("passw")
    u = request.form.get("uname")
    u = u.lower()
    profileRow = getUserProfile(u)
    if(len(profileRow) > 0):
        if(len(profileRow[0]) > 2): #password hash found
            #to forward hash and store in gsheet
            if(profileRow[0][2] == ''): #password blank
                #for reg
                return render_template('login.html', username=u, firstLogin=True)
            else:
                if(encrypt(p) == profileRow[0][2]): #check password
                    #password matched.
                    session["x-token"] = secrets.token_hex(16) #generate token
                    session["x-uname"] = u
                    upsert_by_name(profileRow[0][1],session["x-token"]) #update local file
                    if(session.get("redirect-to")):
                        return redirect(session["redirect-to"])
                    else:
                        return redirect("/")
                else:
                    #password error
                    return render_template('login.html', username='', firstLogin=False, loginFailed=True, message="Invalid username or password")
        else: #for reg
            return render_template('login.html', username=u, firstLogin=True, loginFailed=False, message="")
    else: 
        return render_template('login.html', username='', firstLogin=False, loginFailed=True, message="Invalid username or password")

@auth.route("/register", methods=['POST'])
def register():
    p = encrypt(request.form.get("passw"))
    u = request.form.get("uname")
    u = u.lower()
    tok = secrets.token_hex(16)
    service = build('sheets', 'v4', credentials=auth.creds)
    profileRow = getUserProfile(u)
    
    if(len(profileRow) > 0):
        ui = profileRow[0][0]
        values = [[ui, u, p,'',datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")]]  
        range_name = f'Auth!{0}{ui}:{4}{ui}' 
        body = {
            'values': values
        }
        service.spreadsheets().values().update(
            spreadsheetId=AUTH_SHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        session["x-token"] = tok
        session["x-uname"] = u
        upsert_by_name(u,tok) #update local file
        if(session.get("redirect-to")):
            return redirect(session["redirect-to"])
        else:
            return redirect("/")
    else:
        return render_template('login.html', username='', firstLogin=True, loginFailed=True, message="Error Registering. Try again later." )

            
    return (profileRow)

def getUserProfile(name_to_filter):
    service = build('sheets', 'v4', credentials=auth.creds)
    result = service.spreadsheets().values().get(spreadsheetId=AUTH_SHEET_ID, range=AUTH_SHEET_RANGE).execute()
    values = result.get('values', [])
    filtered_values = [row for row in values if row and row[1] == name_to_filter]
    #ndate = datetime.datetime.now() + datetime.timedelta(days=-1) #datetime.strptime(date_string, "%Y-%m-%d")
    
    # if session.get("isadmin") == None:
    #     # Filter by name
    #     filtered_values = [row for row in values if row and row[1] == name_to_filter and datetime.datetime.strptime(row[3], "%Y-%m-%d") >= ndate]
    # else:
    #     filtered_values = [row for row in values if row and datetime.datetime.strptime(row[3], "%Y-%m-%d") >= ndate]
    
    
    
    # for row in filtered_values:
    #     row.append(datetime.datetime.strptime(row[3], '%Y-%m-%d').strftime('%A'))
    return filtered_values




