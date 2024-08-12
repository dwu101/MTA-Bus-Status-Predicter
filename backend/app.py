from flask import Flask, g, jsonify, request,make_response
import os
from datetime import datetime, timedelta
from flask_cors import CORS
from addDataToPG import getAll
import re
from collections import OrderedDict


app = Flask(__name__)
CORS(app, origins='http://localhost:3000')


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.teardown_appcontext
def close_connection(exception):
    pass

@app.route('/getAccuracies',methods=['POST', 'OPTIONS'])
def getData():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    
    date = request.get_json()['date']
    if date == "all":
        rows = getAll(False)
        ret = {}
        for item in rows[0]:
            # print(item, "\n")
            ret[item[0].strftime("%Y-%m-%d")] = item[1]

    return ret

@app.route('/getFeatures', methods=['GET', 'OPTIONS'])
def getFeatures():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    
    rows = getAll(False)
    result = {}
    feature_counts = {}

    for item in rows:
        feature_string = item[2][2]
        # print(feature_string)

        # Extract features and their importance
        features = re.findall(r'([^,]+),(\d+\.\d+)', feature_string)

        for feature, importance in features:
            feature = feature.strip()
            importance = float(importance)
            
            if importance > 0.01:
                if feature not in result:
                    result[feature] = 0
                    feature_counts[feature] = 0
                
                result[feature] += importance
                feature_counts[feature] += 1

    # Calculate averages
    for feature in result:
        result[feature] /= feature_counts[feature]

    sorted_result = OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    # print(sorted_result)
    sorted_list = [{"feature": k, "importance": v} for k, v in sorted_result.items()]

    return jsonify(sorted_list)

    










@app.route('/')
def home():

    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
