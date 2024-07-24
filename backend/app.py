from flask import Flask, g, jsonify, request,make_response
from getFilesFromGD import getFilesFromGD
from model2 import mainModel, getMostImportantFeatures
from getCurrTime import getCurrTime
import sqlite3
import os
from datetime import datetime, timedelta
from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

DATABASE = 'database.db'
def getDB():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute('PRAGMA foreign_keys = ON') 
    return db

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def modelIsUpdated():
    if os.path.exists("model.pth"):
        mod_time = os.path.getmtime("model.pth")
        mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')

        today = datetime.now().date()
        
        return mod_date == today #since model is updated daily, model is not updated if it was not updated today
    else:
        return False
    
def get_next_id(cursor, date):
    cursor.execute("SELECT MAX(id) FROM dailyData WHERE date = ?", (date,))
    max_id = cursor.fetchone()[0]
    return (max_id or 0) + 1

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

    if os.path.isfile("combined.csv"):
        os.remove("combined.csv")

@app.route('/getData',methods=['POST', 'OPTIONS'])
def getData():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    print("printing request body")
    print(request.get_json())
    date = request.get_json()['date']
    db = getDB()

    if date == "all":
        print("X")
        cursor = db.cursor()
        query = "SELECT date, id, accuracy, feature FROM dailyData"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        
        data = {}
        
        for row in rows:
            date, _, accuracy, feature = row
            
            if date not in data:
                data[date] = {
                    'date': date,
                    'accuracy': accuracy,
                    'features': []
                }
            
            data[date]['features'].append(feature)
        
        db.close()
        print(data)
        return jsonify(data)
        
    elif datetime.strptime(date, '%m/%d/%Y'):
        pass
    else:
        return 404, 'Please enter a valid date in the format mm/dd/yyyy'
    
    db.close()
    return 404, 'idk what error'




@app.route('/runModel', methods=['POST'])
def runModel():
    if modelIsUpdated():
        if os.path.isfile("combined.csv"):
            os.remove("combined.csv")
        return 200, 'model is updated'
    else:
        accuracy = mainModel()
        mostImportantFeatures = getMostImportantFeatures()
        db = getDB()
        cursor = db.cursor()
        date, _ = getCurrTime()
        for feature in mostImportantFeatures:
            next_id = get_next_id(cursor, date)
            cursor.execute("INSERT INTO dailyData (date, id, accuracy, feature) VALUES (?, ?, ?, ?)", 
                   (date, next_id,accuracy, feature))
        db.commit()
        db.close()
        

        # return [accuracy, mostImportantFeatures]
        return 200, 'added data'





@app.route('/')
def home():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dailyData
                  (date TEXT,
                   id INTEGER,
                   accuracy REAL,
                   feature TEXT NOT NULL,
                   PRIMARY KEY (date, id))
        ''')
        conn.commit()
        conn.close()
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
