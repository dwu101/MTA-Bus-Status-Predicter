import requests
import csv
from datetime import datetime
from settings import MTAapiKey, allBusInfoAPI, allStopsAPI, weatherAPI, weatherAPIKey
from afterTime import afterTime
from isWeekend import isWeekend
from getCurrTime import getCurrTime

#time, direction, isweekend, after 10, 12am-6am, passenger count, stop # of next stop on route, feelslike, visibility, windgust, precip, snow, conditions, late?
def dataCollection(filename):
    try: 
        params = {'key': MTAapiKey}

        allBusInfo = requests.get(allBusInfoAPI, params=params)
        if allBusInfo.status_code == 200:
            allBusInfo = allBusInfo.json()
        else:
            raise Exception("All Bus Info API didn't work") #if this doesnt work then break the whole thing

        for item in allBusInfo["Siri"]["ServiceDelivery"]["VehicleMonitoringDelivery"][0]["VehicleActivity"]:
            dataToAdd = []
            # Process monitored vehicle journey data
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

            # Get weather information o
            weather = requests.get(weatherAPI.format(date=date, time=time, key=weatherAPIKey))
            if weather.status_code == 200:
                weather = weather.json()
            else:
                raise Exception("Weather API did not work") #if this doesnt work then break the whole thing
            
            for hour in weather['days'][0]['hours']:
                if hour['datetime'][:2] == time[0:2]: #if the hour is the same, hourly weather
                    try:
                        dataToAdd.append(hour['feelslike'])
                    except Exception:
                        dataToAdd.append("")
                    
                    try:
                        dataToAdd.append(hour['visibility'])
                    except Exception:
                        dataToAdd.append("")
                    
                    try:
                        dataToAdd.append(hour['windgust'])
                    except Exception:
                        dataToAdd.append("")
                    
                    try:
                        dataToAdd.append(hour['precip'])
                    except Exception:
                        dataToAdd.append("")
                    
                    try:
                        dataToAdd.append(hour['snow'])
                    except Exception:
                        dataToAdd.append("")
                    
                    try:
                        dataToAdd.append(hour['conditions'])
                    except Exception:
                        dataToAdd.append("") 

                    break #only need to do once

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

            # print(dataToAdd)
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(dataToAdd)

            
        return 200, "data added to file" 
    except Exception as e:
        return 400, e

    








            


