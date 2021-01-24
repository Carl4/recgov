"""
These classes interface with select components in the recreation.gov API.

"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pprint import pprint

from dateutil.parser import parse
from yaml import FullLoader, load

from .filters import AvailabilityFilters
from .utils import next_month, represents_int, this_month
from ._requests import get_anonymous_session

API_URL = "https://www.recreation.gov/api/recommendation/recommend"

sess = get_anonymous_session()
class Availability():
    """This class  uses the month api to obtain availability information for a campground.
    """
    _URL_MONTH = "https://www.recreation.gov/api/camps/availability/campground/{asset_id}/month"
    _CLICK_URL = "https://www.recreation.gov/camping/campgrounds/{asset_id}"

    def __init__(self, asset_id: int, filters=None, headers=None):
        self.asset_id = asset_id
        self.filters = filters

    def check(self):
        """Checks all months and returns their results as a dict

        :raises RuntimeError: If required filters missing (must have a start_date). 
        :yield: month string, dict 
        :rtype: Iterator[(str, dict)]
        """
        if 'start_date' in self.filters:
            sd = self.filters['start_date']
            start_month = datetime(sd.year, sd.month, 1)
        else:
            raise RuntimeError("I need a start_date to know when to search!")
        if 'end_date' in self.filters:
            ed = self.filters['end_date']
            end_month = datetime(ed.year, ed.month, 1)
        else:
            # If there's no end_month, don't go forever.
            end_month = next_month(start_month)

        mo = start_month
        while mo <= end_month:
            yield mo.strftime("%Y-%m"), self.check_month(mo)
            mo = next_month(mo)

    def get_month_dict(self, month: datetime) -> dict:
        """Gets the month json object

        :param month: The month to get (day, hour, minute, and second squashed)
        :type month: datetime
        :return: The monthly availability data object
        :rtype: dict
        """
        # Clobber day, hour, minute, second
        if not all([month.day == 1, month.hour == 0, month.minute == 0, month.second == 0]):
            raise ValueError("Month must have day=1 and h/m/s=0")
        params = {'start_date': month.isoformat() + ".000Z"}
        resp = sess.get(self._URL_MONTH.format(asset_id=self.asset_id), params=params)
        return resp.json()

    def check_month(self, month: datetime) -> list:
        """Checks a month for availabilities

        :param month: The month to check.
        :type month: datetime
        :return: List of sites that are available, if any.
        :rtype: list
        """
        objs = self.get_month_dict(month)
        filt = AvailabilityFilters(self.filters)
        return filt.filter(objs)['campsites']


