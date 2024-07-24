import datetime

def afterTime(hour): #return True if today is weekend. False otherwise
    curr = datetime.datetime.now().time()
    ten_pm = datetime.time(hour, 0, 0)
    return curr > ten_pm

# print(isWeekend())


