import time, datetime


class TimeRange(object):
    @classmethod
    def get_today(cls, date_query):
        if date_query and isinstance(date_query, basestring):
            mon, day, year = map(int, date_query.split("/"))
        elif isinstance(date_query, datetime.datetime):
            year, mon, day = date_query.utctimetuple()[:3]
        else:
            year, mon, day = time.localtime()[:3]
        return year, mon, day

    @classmethod
    def get_one_day_range(cls, date_query):
        start = datetime.datetime(*cls.get_today(date_query))
        start = start + datetime.timedelta(seconds=-1)
        end = start + datetime.timedelta(days=1)
        return [start, end]

    @classmethod
    def get_one_week_range(cls, date_query):
        start = datetime.datetime(*cls.get_today(date_query))
        start = start - datetime.timedelta(days = start.isoweekday() % 7)
        end = start + datetime.timedelta(days=7, seconds=-1)
        return [start, end]

    @classmethod
    def get_one_month_range(cls, date_query):
        year, month = cls.get_today(date_query)[:2]
        start = datetime.datetime(year, month, 1)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        end = datetime.datetime(year, month, 1) + datetime.timedelta(seconds=-1)
        return [start, end]


class OneDay(TimeRange):
    get = TimeRange.get_one_day_range
    get_week = TimeRange.get_one_week_range


class OneWeek(TimeRange):
    get = TimeRange.get_one_week_range
    get_week = TimeRange.get_one_week_range


class OneMonth(TimeRange):
    get = TimeRange.get_one_month_range


def now():
    return datetime.datetime.now()


def today():
    return datetime.datetime(*time.localtime()[:3])


def tomorrow():
    datetime.datetime(*time.localtime()[:3]) + datetime.timedelta(days=1)


def next_week():
    start, end = OneWeek.get(now())
    return end + datetime.timedelta(seconds=1)

def next_dayofweek(dayofweek, start=None):
    target_day_numbers = {"sunday":6, "monday":0, "tuesday":1, "wednesday":2,
        "thursday":3, "friday":4, "saturday":5, "everyday":None}
    if start is None:
        start = today()
    else:
        start += datetime.timedelta(days=1)
    target_day = target_day_numbers[dayofweek]
    if target_day is None:
        return start
    result = start
    while result.weekday() != target_day:
        result += datetime.timedelta(days=1)
    return result

