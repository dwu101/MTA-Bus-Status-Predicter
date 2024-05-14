import datetime
def getCurrTime():
    currTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")
    return currTime[0], currTime[1]
    