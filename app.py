import csv
import time
import os
from dataCollection import dataCollection
from getCurrTime import getCurrTime
from uploadFileToGD import uploadFileToGD
from settings import folderID


date, _ = getCurrTime()
filename = date + "_B52.csv"
columns = ["time", "direction", "isweekend"," after 10"," 12am-6am"," passenger count"," stop # of next stop on route", "feelslike", "visibility", "windgust", "precip", "snow", "conditions", "late"]

if not os.path.exists(filename): #if the file exists, then don't create. useful for if things were to break unexpectedly
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)

while True:

    code, message = dataCollection(filename)
    if code == 404:
        print(message)
        break

    dateNow, _ = getCurrTime()

    if date != dateNow: #new day
        uploadFileToGD(filename, folderID) #upload the csv file
        os.remove(filename) #remove the csv

        filename = dateNow + "_B52.csv" #new file name
    
        with open(filename, mode='w', newline='') as file: #create the new file
            writer = csv.writer(file)
            writer.writerow(columns)
        
        date = dateNow
    print("going good! >:)")
    time.sleep(60) #collect data every minute.
        

