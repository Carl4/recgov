"""Just a place to put some handy utility functions.
"""
from datetime import datetime, timedelta

# To find the next month easily: Add 31 days, then truncate back to day 1.
def this_month(month:datetime) -> datetime:
    """Find the first day of this month given a datetime.

    :param month: the date
    :type month: datetime
    :return: The first day of the month.
    :rtype: datetime
    """
    return datetime(month.year, month.month, 1)


_A_MONTH = timedelta(days=31)                                                                                                                                          
def next_month(month:datetime) -> datetime:
    """Find the first day of the next month given a datetime.

    :param month: the date
    :type month: datetime
    :return: The first day of the next month.
    :rtype: datetime
    """
    dt = this_month(month)
    return datetime((dt+_A_MONTH).year, (dt+_A_MONTH).month, 1) 

def tokenize(string: str) -> [str]:
    """Tokenize a string.

    :param string: [description]
    :type string: str
    """
    return string.split(" ")

def represents_int(s:str) -> bool: 
    """Checks if a string can be an integer

    :param s: [description]
    :type s: str
    :raises RuntimeError: [description]
    :raises ValueError: [description]
    :return: [description]
    :rtype: bool
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

