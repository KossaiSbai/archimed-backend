import calendar
import datetime
import re

def validate_input(regex, input):
    return re.match(regex, input) is not None

def days_in_year(year=datetime.datetime.now().year):
    return 365 + calendar.isleap(year)