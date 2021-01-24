from ._requests import get_session
from json import dumps

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
    def permitted_equipment_lengths(self):
        return {x['EquipmentName']: x['MaxLength'] for x in self['PERMITTEDEQUIPMENT']}

    def supports_equipment(self, equipment_name: str, equipment_length: float) -> bool:
        return self.permitted_equipment_lengths.get(equipment_name, -1) > equipment_length
    
    def __repr__(self):
        return f"<campsite id={dumps(self.id)} name={dumps(self.name)} type={dumps(self.site_type)} " + \
               f"facility={dumps(self['FacilityID'])} loop={dumps(self.loop)} />"


class CampsiteSet(dict):
    """A set of Campsite objects indexed on their site id.
    """

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
        return CampsiteSet({x['CampsiteID']: x for x in self.values()
                            if x.supports_equipment(equipment_name, equipment_length)})

    @property
    def unique_campsite_types(self):
        return set([x['CampsiteType'] for x in self.values()])
    
    def filter_by_campsite_type(self, types: (list, set)) -> 'CampsiteSet':
        """Returns a smaller set filtered by the campsite type(s)

        :param types: a list, tuple, or set of types
        :return: The filtered set
        :rtype: CampsiteSet
        """
        return CampsiteSet({x['CampsiteID']: x for x in self.values()
                            if x['CampsiteType'] in types})

    def exclude_by_campsite_type(self, types: (list, set)) -> 'CampsiteSet':
        """Returns a smaller set by excluding by the given campsite type(s)

        :param types: a list, tuple, or set of types
        :return: The filtered set
        :rtype: CampsiteSet
        """
        return CampsiteSet({x['CampsiteID']: x for x in self.values()
                            if x['CampsiteType'] not in types})



def get_campsites(asset: int) -> CampsiteSet:
    """Gets a CampsiteSet for the given asset.

    :param asset: the asset id from recreation.gov
    :type asset: int
    :return: a CampsiteSet you can filter.
    :rtype: CampsiteSet
    """
    sess = get_session()
    resp = sess.get_record_iterator(
        f"https://ridb.recreation.gov/api/v1/facilities/{asset}/campsites")
    return CampsiteSet({x['CampsiteID']: Campsite(x) for x in resp})
