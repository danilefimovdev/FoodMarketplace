from datetime import datetime


def get_today_day():

    now = datetime.now()
    day = datetime.isoweekday(now)
    return day
