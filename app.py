import csv
import time
import os
from dataCollection import dataCollection
from getCurrTime import getCurrTime
from uploadFileToGD import uploadFileToGD
from settings import folderID


date, _ = getCurrTime()
filename = date + "_B52.csv"
columns = ["time", "direction", "isweekend","after 10","12am-6am","passenger count","stop # of next stop on route", "feelslike(f)", "visibility(mi)", "windgust(mph)", "precip(in)", "uv", "humidity", "conditions", "late"]

if not os.path.isfile(filename): #if the file exists, then don't create. useful for if things were to break unexpectedly
    print("creating new file")
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
    print("new file created")

print("loop starting")
while True:
    code, message = dataCollection(filename)
    if code == 404:
        print(message)
        break

    dateNow, _ = getCurrTime()

    if date != dateNow: #new day
        code, message = uploadFileToGD(filename, folderID) #upload the csv file
        if code == 404:
            print(e)
            break
        print("FILE UPLOADED")
        os.remove(filename) #remove the csv

        filename = dateNow + "_B52.csv" #new file name

        with open(filename, mode='w', newline='') as file: #create the new file
            writer = csv.writer(file)
            writer.writerow(columns)
            print("NEW FILE CREATED")
        
        date = dateNow

        
    print("going good! >:)")
    time.sleep(300) #collect data every 5 minutes.
        

