"""Classes that support filtering of dictionaries.
"""
from datetime import datetime, timedelta
from .utils import tokenize, represents_int


class AvailabilityFilters():
    datefmt = '%Y-%m-%dT%H:%M:%SZ'
    DEFAULT_FILTERS = [
        ('available', True),
    ]
    def __init__(self, filters: dict):
        self.filters = list(filters.items()) + self.DEFAULT_FILTERS
    
    def filter(self, obj: dict) -> dict:
        for filter in self.filters:
            self._apply_filter(filter, obj)
        return obj

    def _apply_filter(self, filter: tuple, obj: dict):
        """Applies a filter an object.

        :param filter: [description]
        :type filter: tuple
        :param obj: [description]
        :type obj: dict
        """
        filter_name, filter_params = filter 
        filter_function = getattr(self, filter_name, None)
        if filter_function is None: 
            raise RuntimeError(f"Unrecognized filter name: {filter_name}")
        filter_function(obj, filter_params)

    def start_date(self, obj, start):
        """Filters the object on start dates

        :param obj: [description]
        :type obj: [type]
        :param start: [description]
        :type start: [type]
        """
        for data in obj['campsites'].values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items()
            if datetime.strptime(k, self.datefmt) >= start }

    def end_date(self, obj, end):
        """Filters the object on end dates

        :param obj: [description]
        :type obj: [type]
        :param start: [description]
        :type start: [type]
        """

        def check_time(time:datetime):
            return datetime.strptime(time, self.datefmt) <= end

        for data in obj['campsites'].values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items() if check_time(k) }

    def available(self, obj, params=True): 
        for data in obj['campsites'].values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items() if v=="Available" }

    def recursive_filter(self, obj: dict, filter):
        if hasattr(obj, 'items'):
            return {k: self.recursive_filter(v, filter) 
                    for k,v in obj.items() if filter(k, v)}
        else:
            return obj
