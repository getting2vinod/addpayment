from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import datetime
from waitress import serve


app = Flask(__name__)
app.secret_key = "thisismyveryloooongsecretkey"

# Initialize Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'myutils-437714-bd0d0a3e77bd.json'  # Update this path
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

Payment_SHEET_ID = '1PJy366Hc5uuN4AhfFS9joP8qPesZJsC9x8FYtlqf6Cs'
Expense_SHEET_ID = '1x2FR_PMfwHM2V5gHu15DsgXHFcqLlXSbRarKyQwcNms'

Payment_RANGE_NAME = 'Accounting!A2:K'  # Adjust range as needed
Expense_RANGE_NAME = 'Expense Tracker!A2:O' 

@app.route('/')
def index():
    session.clear()
    lastref = getlastref()
    lastrefnum=int(lastref[0])+1
    return render_template('home.html',paydate=datetime.datetime.now().strftime("%Y-%m-%d"),nextpayref=lastrefnum,summary=lastref[3] + " - " + lastref[4] + " - " + lastref[8])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')

def getlastref():
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=Expense_SHEET_ID, range=Expense_RANGE_NAME).execute()
    values = result.get('values', [])
    #ndate = datetime.datetime.now() + datetime.timedelta(days=-1) #datetime.strptime(date_string, "%Y-%m-%d")
    
    # if session.get("isadmin") == None:
    #     # Filter by name
    #     filtered_values = [row for row in values if row and row[1] == name_to_filter and datetime.datetime.strptime(row[3], "%Y-%m-%d") >= ndate]
    # else:
    #     filtered_values = [row for row in values if row and datetime.datetime.strptime(row[3], "%Y-%m-%d") >= ndate]
    
    
    
    # for row in filtered_values:
    #     row.append(datetime.datetime.strptime(row[3], '%Y-%m-%d').strftime('%A'))



    values.sort(key=lambda x: int(x[0]))
    
    return values[len(values)-1]


@app.route('/saved', methods=['GET'])
def saved():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    session.clear()
    name_to_filter = request.form['mobile']
    passkey = request.form.get("passkey")
    service = build('sheets', 'v4', credentials=creds)
    if(passkey):       
       result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=ADMIN_RANGE_NAME).execute()
       values = result.get('values', [])
       filtered_values = [row for row in values if row and row[0] == name_to_filter]
       if filtered_values and passkey == filtered_values[0][1]:
           session["isadmin"] = True
    session["name_to_filter"] = name_to_filter
    return redirect('/list')

# @app.route('/list', methods=['GET'])
# def new_and_list():
#     filtered_values = build_list(name_to_filter=session['name_to_filter'])    
#     return render_template('home.html', filtered_values=filtered_values, mobile=session['name_to_filter'], is_admin=session.get('isadmin'))

@app.route('/delete', methods=['POST'])
def delete():
    row = request.form['delrowid']
    column = "G" #will be fixed for row
    new_value = 'Cancelled'
    mobile = request.form['delrowmobile']

    service = build('sheets', 'v4', credentials=creds)
    range_name = f'Sheet1!{column}{row}'  # Example: "Sheet1!A2"

    body = {
        'values': [[new_value]]
    }

    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

    return redirect('/list')

@app.route('/addpayment', methods=['POST'])
def addpayment():
    try:
        payref = request.form['payref']
        paydate = request.form['paydate']
        payby = request.form['payby']
        paybank = request.form['paybank']
        payto = request.form['payto']
        payoutofcontract = request.form.getlist('payoutofcontract')
        paytowards = request.form['paytowards']
        paymethod = request.form['paymethod']
        payasexpense = request.form.getlist('payasexpense')
        payamount = request.form['payamount']
        payspecialnotes = request.form['payspecialnotes']
        paydetails = request.form['paydetails']
        
        service = build('sheets', 'v4', credentials=creds)

        paydate = (datetime.datetime.strptime(paydate,("%Y-%m-%d"))).strftime("%d/%m/%Y")
        #saving into expense
        #=if(or(mid(G139,1,5)="Mom",mid(G139,1,5)="Dad"),"Kurup",mid(G139,1,5))
        fforbyref= '=if(or(mid(INDIRECT(ADDRESS(row(),column()-1)),1,5)="Mom",mid(INDIRECT(ADDRESS(row(),column()-1)),1,5)="Dad"),"Kurup",mid(INDIRECT(ADDRESS(row(),column()-1)),1,5))'
        fforsum = '=INDIRECT(ADDRESS(row(),column()-2)) + INDIRECT(ADDRESS(row()-1,column()))'
        values = [[payref, paytowards, paydetails, payto, paydate, paymethod,payby+' - '+paybank,fforbyref,payamount,'',fforsum,'',payspecialnotes]]  
        
        print(values)
        body = {
            'values': values
        }
        service.spreadsheets().values().append(
            spreadsheetId=Expense_SHEET_ID,
            range=Expense_RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()


        if('on' in payasexpense) == False:
            if('on' in payoutofcontract):
                payoc = payamount
                payamount=''
            else:
                payoc = ''
            fforEba = '=INDIRECT(address(row()-1,column())) + (INDIRECT(address(row(),column()-2)) - INDIRECT(address(row(),column()-1)))'
            fforCheck = '=INDIRECT(address(row()-1,column()))'
            valuespay = [[paydate, payby, payto, paytowards, paymethod,payref,payamount,payoc,fforEba,'',payspecialnotes]]  
            body = {
                'values': valuespay
            }
            service.spreadsheets().values().append(
                spreadsheetId=Payment_SHEET_ID,
                range=Payment_RANGE_NAME,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
        summary = "Saved successfully !!!"
    except Exception as err:
        summary = f"Failed {err}"


        #save into payment as well
        

    
    #status_val = '=if(INDIRECT(ADDRESS(row(),column()+1))="","Pay Now",if(INDIRECT(ADDRESS(row(),column()+3)),"Confirmed","Approval Pending"))'
   

    return render_template('index.html', summary=summary)

@app.route('/confirm', methods=['POST'])
def update_confirm():
    row = request.form['confirmrowid']     
    columnApproval = "J" #will be fixed for row for approval checkbox
   
    service = build('sheets', 'v4', credentials=creds)
       
    #can be improved with one call
    rangeApproval_name = f'Sheet1!{columnApproval}{row}' 
    bodyApproval = {
        'values': [[True]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=rangeApproval_name,
        valueInputOption='RAW',
        body=bodyApproval
    ).execute()
    return redirect('/list')
    
@app.route('/paymentconfirm', methods=['POST'])
def update_payment():
    row = request.form['payrowid']
    column = "H" #will be fixed for row
    columnApproval = "J" #will be fixed for row for approval checkbox
    new_value = request.form['payref']
    mobile = request.form['payrowmobile']

    service = build('sheets', 'v4', credentials=creds)
    range_name = f'Sheet1!{column}{row}'  # Example: "Sheet1!A2"

    body = {
        'values': [[new_value]]
    }

    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

    #can be improved with one call
    rangeApproval_name = f'Sheet1!{columnApproval}{row}' 
    bodyApproval = {
        'values': [[False]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=rangeApproval_name,
        valueInputOption='RAW',
        body=bodyApproval
    ).execute()

    return redirect('/list')

if __name__ == '__main__':
    #app.run(debug=True, host="0.0.0.0", port=5000)
    serve(app, host='0.0.0.0', port=5000)
