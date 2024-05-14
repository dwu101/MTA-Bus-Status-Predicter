import datetime

def isWeekend(): #return True if today is weekend. False otherwise
    today = datetime.date.today().weekday()
    return today == 5 or today == 6

# print(isWeekend())


