from model2 import mainModel, getMostImportantFeatures 
from getCurrTime import getCurrTime
from addDataToPG import addDataToPG
import schedule
import time

def main():
    date, _ = getCurrTime()
    newAcc = mainModel()
    features = getMostImportantFeatures()
    features = ','.join(f"{key},{value}" for key, value in features.items())
    addDataToPG(date, newAcc, features)
    return 




# Schedule the job to run at 12:30 AM
schedule.every().day.at("00:30").do(main)

while True:
    schedule.run_pending()
    time.sleep(30)
