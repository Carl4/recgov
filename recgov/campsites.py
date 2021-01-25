from datetime import date
from itertools import groupby
from json import dumps
from operator import itemgetter

from ._requests import get_session


class Campsite(dict):

    @property
    def id(self):
        return self['CampsiteID']

    @property
    def name(self):
        return self['CampsiteName']

    @property
    def site_type(self):
        return self['CampsiteType']

    @property
    def loop(self):
        return self['Loop']

    @property
    def attributes(self):
        return {x['AttributeName']: x['AttributeValue'] for x in self['ATTRIBUTES']}

    @property
    def availabilities(self):
        avail = [date.fromisoformat(k[:10])
                 for k, v in self.get('availabilities', {}).items()
                 if v == "Available"]
        # Consolidate to ranges of dates. Adapted from
        #   See https://docs.python.org/2.6/library/itertools.html#examples

        def delta(ndx):
            return ndx[0] - ndx[1].toordinal()

        consecutive_days = [[x[1] for x in g]
                            for k, g in groupby(enumerate(avail), delta)]

        def cleanup_sets(dayset: list) -> str:
            if len(dayset) == 1:
                return dayset[0].isoformat()
            return dayset[0].isoformat() + " to " + dayset[-1].isoformat()

        return [cleanup_sets(x) for x in consecutive_days]

    @property
    def available_nights(self) -> int:
        """Returns the number of available nights

        :return: Number of nights available
        :rtype: int
        """
        avail = [x for x in self.get(
            'availabilities').values() if x == "Available"]
        if avail is not None:
            return len(avail)

    @property
    def permitted_equipment_lengths(self):
        return {x['EquipmentName']: x['MaxLength'] for x in self['PERMITTEDEQUIPMENT']}

    def supports_equipment(self, equipment_name: str, equipment_length: float) -> bool:
        return self.permitted_equipment_lengths.get(equipment_name, -1) > equipment_length

    def __repr__(self):
        availabilities = f" availabilities={dumps(self.availabilities)} "
        return f"<campsite id={dumps(self.id)} name={dumps(self.name)} type={dumps(self.site_type)} " + \
               f"facility={dumps(self['FacilityID'])} loop={dumps(self.loop)} {availabilities}/>"

    @property
    def site_url(self):
        return f"https://www.recreation.gov/camping/campsites/{self.id}"

    def __gt__(self, other: "Campsite") -> bool:
        return self.loop+self.name > other.loop+other.name

    def __lt__(self, other: "Campsite") -> bool:
        return self.loop+self.name < other.loop+other.name


class CampsiteSet(dict):
    """A set of Campsite objects indexed on their site id.
    """

    def ingest_availability(self, availability: dict) -> None:
        """ingests availability data to the campsites.

        :param availability: a dictionary of availability date from the month endpoint.
        :type availability: dict
        """
        for k, v in availability.items():
            if k in self:
                self[k]['availabilities'] = v['availabilities']

    @staticmethod
    def from_list(campsites: list) -> 'CampsiteSet':
        """Geerates a CampsiteSet from a list.

        :return: [description]
        :rtype: [type]
        """
        return CampsiteSet({x['CampsiteID']: Campsite(x) for x in campsites})

    def filter_by_equipment(self, equipment_name: str, equipment_length: float) -> 'CampsiteSet':
        """Returns a smaller CampsiteSet that supports the given equipment.

        :return: the filtered set of campsites based on the specified equipment
        :rtype: CampsiteSet
        """
        return CampsiteSet({x['CampsiteID']: Campsite(x) for x in self.values()
                            if x.supports_equipment(equipment_name, equipment_length)})

    @property
    def unique_campsite_types(self):
        return set([x['CampsiteType'] for x in self.values()])

    def filter_by_campsite_type(self, *types) -> 'CampsiteSet':
        """Returns a smaller set filtered by the campsite type(s)

        :param types: a list, tuple, or set of types
        :return: The filtered set
        :rtype: CampsiteSet
        """
        return CampsiteSet({x['CampsiteID']: Campsite(x) for x in self.values()
                            if x['CampsiteType'] in types})

    def exclude_by_campsite_type(self, *types) -> 'CampsiteSet':
        """Returns a smaller set by excluding by the given campsite type(s)

        :param types: a list, tuple, or set of types
        :return: The filtered set
        :rtype: CampsiteSet
        """
        return CampsiteSet({x['CampsiteID']: Campsite(x) for x in self.values()
                            if x['CampsiteType'] not in types})

    def apply_filters(self, filters: dict) -> 'CampsiteSet':
        result = self
        for filter, params in filters.items():
            if not hasattr(self, filter):
                raise ValueError(f"Unknown filter, {filter}")
            result = getattr(result, filter)(
                *params.get('args', []), **params.get('kwargs', {}))
        return CampsiteSet(result)

    def with_availability(self) -> 'CampsiteSet':
        return CampsiteSet({k: v for k, v in self.items()
                            if v.available_nights > 0})


def get_campsites(asset: int, apikey=None) -> CampsiteSet:
    """Gets a CampsiteSet for the given asset.

    :param asset: the asset id from recreation.gov
    :type asset: int
    :param apikey: An API Key if you haven't set the environment variable
    :type apikey: str
    :return: a CampsiteSet you can filter.
    :rtype: CampsiteSet
    """
    sess = get_session(apikey=apikey)
    resp = sess.get_record_iterator(
        f"https://ridb.recreation.gov/api/v1/facilities/{asset}/campsites")
    return CampsiteSet({x['CampsiteID']: Campsite(x) for x in resp})
