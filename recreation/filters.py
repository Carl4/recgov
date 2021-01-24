"""Classes that support filtering of dictionaries.
"""
from datetime import datetime, timedelta
from .utils import tokenize, represents_int


class Filters():
    datefmt = '%Y-%m-%dT%H:%M:%SZ'
    DEFAULT_FILTERS = [
        ('available', True),
        ('has_availability', True),
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

    def campsite_type__contains_any(self, obj, params):
        """Only keep campsites where `campsite_type` contains any of the strings in params

        Matches words only (splits on a " ")

        :param obj: [description]
        :type obj: [type]
        :param params: [description]
        :type params: [type]
        """
        if not isinstance(params, (list,)):
            ValueError("campsite_type__contains_any value must be a list.")

        # Sorry about this nested list composition. I know it's tricky to grock.
        # Basically, it only includes campsites in the list if campsite_type contains
        # any of the params to thie filter.
        obj['campsites'] = {k:v for k,v in obj['campsites'].items() 
                            if any([val in tokenize(v['campsite_type']) 
                                    for val in params])
                            }

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

    def site_is_integer(self, obj, params=True):
        obj['campsites'] = {k:v for k,v in obj['campsites'].items() if represents_int(v['site'])==params }

    def available(self, obj, params=True): 
        for data in obj['campsites'].values():
            data['availabilities'] = {k:v for k,v in data['availabilities'].items() if v=="Available" }

    def has_availability(self, obj, params=True):
        """Delete unavailable sites
        """
        obj['campsites'] = {k:v for k,v in obj['campsites'].items()
                    if len(v['availabilities'])}

    def filter_by_name(self, obj: dict, keyname: str, filter):
        """Filters all values corresponding to keys with name

        :param obj: The object to recursively filter
        :type obj: dict
        :param keyname: Key Name to trigger filter
        :type keyname: str
        :param filter: Function to apply to value
        :type filter: function
        """


    def recursive_filter(self, obj: dict, filter):
        if hasattr(obj, 'items'):
            return {k: self.recursive_filter(v, filter) 
                    for k,v in obj.items() if filter(k, v)}
        else:
            return obj
