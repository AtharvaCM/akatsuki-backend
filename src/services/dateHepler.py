from datetime import date
import datetime

# todays date
today = date.today()


def getCurrentDate(dateString):
    return today.strftime(dateString)


def getNextDate(dateString):
    nextDate = date.today() + datetime.timedelta(days=1)
    return nextDate.strftime(dateString)
