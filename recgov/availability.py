"""
These classes interface with select components in the recreation.gov API.

"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from ._requests import get_anonymous_session
from .campsites import Campsite, get_campsites
from .utils import next_month, represents_int, this_month

API_URL = "https://www.recreation.gov/api/recommendation/recommend"

sess = get_anonymous_session()
class Availability(dict):
    """This class  uses the month api to obtain availability information for a campground.
    """
    _URL_MONTH = "https://www.recreation.gov/api/camps/availability/campground/{asset_id}/month"
    _CLICK_URL = "https://www.recreation.gov/camping/campgrounds/{asset_id}"
    datefmt = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, asset_id: int, headers=None):
        self.asset_id = asset_id
        self.campsites = get_campsites(asset_id)
        super().__init__()

    def apply_filters(self, filters: dict):
        """Checks all months  for availability, filters the result, and returns their results as a dict

        :raises RuntimeError: If required filters missing (must have a start_date). 
        :yield: month string, dict 
        :rtype: Iterator[(str, dict)]
        """
        if 'start_date' in filters:
            sd = filters['start_date']
            start_month = datetime(sd.year, sd.month, 1)
        else:
            raise RuntimeError("I need a start_date to know when to search!")
        if 'end_date' in filters:
            ed = filters['end_date']
            end_month = datetime(ed.year, ed.month, 1)
        else:
            # If there's no end_month, don't go forever.
            end_month = next_month(start_month)

        mo = start_month
        
        while mo <= end_month:
            self.retrieve_month(mo, filters)
            mo = next_month(mo)
        return self.filter(filters)

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

    def merge_availabilities(self, other):
        for k,v in other.items():
            if k in self:
                if 'availabilities' in self[k]:
                    self[k]['availabilities'].update(v['availabilities'])
                else:
                    self[k].merge(v)
            else:
                self[k] = Campsite(v)

    def retrieve_month(self, month: datetime, filters: dict) -> list:
        """Retrieves availabilities for a month

        :param month: The month to check.
        :type month: datetime
        :return: List of sites that are available, if any.
        :rtype: list
        """
        self.merge_availabilities(self.get_month_dict(month)['campsites'])

    def filter(self, filters: dict):
        obj = self
        for filter in filters.items():
            obj = obj._apply_filter(filter)
        return obj

    def _apply_filter(self, filter: tuple):
        """Applies a filter an object.

        :param filter: [description]
        :type filter: tuple
        :param obj: [description]
        :type obj: dict
        """
        filter_name, filter_params = filter 
        filter_function = getattr(self, f"filter_{filter_name}", None)
        if filter_function is None: 
            raise RuntimeError(f"Unrecognized filter name: {filter_name}")
        return filter_function(filter_params)

    def filter_start_date(self, start):
        """Filters the object on start dates

        :param start: [description]
        :type start: [type]
        """        
        obj = deepcopy(self)
        for data in obj.values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items()
            if datetime.strptime(k, self.datefmt) >= start }
        return obj

    def filter_end_date(self, end:datetime):
        """Filters the object on end dates

        :param start: [description]
        :type start: [type]
        """
        obj = deepcopy(self)

        def check_time(time:datetime):
            return datetime.strptime(time, self.datefmt) <= end

        for data in obj.values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items() if check_time(k) }

        return obj

