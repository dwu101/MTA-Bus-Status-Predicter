import requests
import csv
import traceback
from datetime import datetime
from settings import MTAapiKey, allBusInfoAPI, allStopsAPI, weatherAPI, weatherAPIKey, XRapidAPIHost, XRapidAPIKey
from afterTime import afterTime
from isWeekend import isWeekend
from getCurrTime import getCurrTime

# columns = ["time", "direction", "isweekend","after 10","12am-6am","passenger count","stop # of next stop on route", "feelslike(f)", "visibility(mi)", "windgust(mph)", "precip(in)", "uv", "humidity", "conditions", "late"]
def dataCollection(filename):
    try: 
        headers = {
            "X-RapidAPI-Key": XRapidAPIKey,
            "X-RapidAPI-Host": XRapidAPIHost
        }
        q = {"q": "Brooklyn"}

        weather = requests.get(weatherAPI, headers=headers, params=q)
        
        if weather.status_code == 200:
            weather = weather.json()['current']
        else:
            message = weather.json()
            print(message)
            raise Exception("Weather API did not work") #if this doesnt work then break the whole thing


        weatherList = []

        try:
            weatherList.append(weather['feelslike_f'])
        except Exception:
            weatherList.append("")
        
        try:
            weatherList.append(weather['vis_miles'])
        except Exception:
            weatherList.append("")
        
        try:
            weatherList.append(weather['gust_mph'])
        except Exception:
            weatherList.append("")
        
        try:
            weatherList.append(weather['precip_in'])
        except Exception:
            weatherList.append("")
        
        try:
            weatherList.append(weather['uv'])
        except Exception:
            weatherList.append("")

        try:
            weatherList.append(weather['humidity'])
        except Exception:
            weatherList.append("")
        
        try:
            weatherList.append(weather['condition']['text'])
        except Exception:
            weatherList.append("") 


        params = {'key': MTAapiKey}
        allBusInfo = requests.get(allBusInfoAPI.format(key=MTAapiKey))
        if allBusInfo.status_code == 200:
            allBusInfo = allBusInfo.json()
        else:
            message = allBusInfo.json()
            print(message)
            raise Exception("All Bus Info API didn't work") #if this doesnt work then break the whole thing
        
        for item in allBusInfo["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["VehicleActivity"]:

            dataToAdd = []
            otherData = item['MonitoredVehicleJourney']
            if otherData['PublishedLineName'] != "B52":  # Only interested in B52 line
                continue
            
            date, time = getCurrTime()
            datePlusTime = date + " " + time

            dataToAdd.append(datePlusTime)
        
            try:
                dataToAdd.append(otherData['DirectionRef'])
            except Exception as e:
                dataToAdd.append("")

            try:
                dataToAdd.append(isWeekend())
            except Exception as e:
                dataToAdd.append("")

            try:
                dataToAdd.append(afterTime(22))
            except Exception as e:
                dataToAdd.append("")

            try:
                dataToAdd.append(afterTime(0) and not afterTime(6))  # Late night hours
            except Exception as e:
                dataToAdd.append("")

            try:
                dataToAdd.append(otherData['MonitoredCall']['Extensions']['Capacities']['EstimatedPassengerCount'])
            except Exception as e:
                dataToAdd.append("")

            allStops = requests.get(allStopsAPI.format(busRoute="B52", key=MTAapiKey)) #get stop information
            if allStops.status_code == 200:
                allStops = allStops.json()
            else:
                message = allStops.json()
                print(message)
                raise Exception("Stop info API didn't work") #if this doesnt work then break the whole thing

            try:
                nextStopID = otherData['MonitoredCall']['StopPointRef']

                for direction in allStops["data"]['entry']['stopGroupings'][0]['stopGroups']:
                    if direction['id'] == otherData['DirectionRef']:
                        count = 1
                        for stopID in direction['stopIds']:
                            if stopID == nextStopID:
                                break
                            count += 1
                        dataToAdd.append(count)
                        break
            except Exception as e:
                dataToAdd.append("")

            dataToAdd += weatherList #add weather information. so I only have to call weather API once for every time dataCollection is called.

            try: #late or not
                aimedArrTime = otherData['MonitoredCall']['AimedArrivalTime']
                estArrTime = otherData['MonitoredCall']['ExpectedArrivalTime']
                aimedArrTime = datetime.fromisoformat(aimedArrTime)
                estArrTime = datetime.fromisoformat(estArrTime)
                diff = estArrTime - aimedArrTime 
                minutes = diff.total_seconds() / 60 
            
                if minutes > 5:
                    dataToAdd.append(1)

                else:
                    dataToAdd.append(0)
            except:
                dataToAdd.append("")


            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(dataToAdd)


        return 200, "data added to file" 
    except Exception as e:
        error = ['error',traceback.format_exc()]
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(error)

        return 200, error #debug, seeing where the error is. change this back to 404 if necessary

    







            


