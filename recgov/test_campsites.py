from .campsites import Campsite, CampsiteSet
from copy import deepcopy
from random import sample

CAMPSITE = {
    "CampsiteID": 1,
    "CampsiteName": "042",
    "CampsiteType": "Spam",
    "Loop": "Ni",
    "FacilityID": "1",
    "ATTRIBUTES": [
        {"AttributeName": "Eric Idle",
            "AttributeValue": "Brave Sir Robin"},
        {"AttributeName": "John Cleese",
            "AttributeValue": "Sir Lancelot"},
        {"AttributeName": "Black Knight Injuries",
            "AttributeValue": "Just a flesh wound."}
    ],
    "availabilities": {
        "2021-01-01T00:00:00Z": "Available",
        "2021-01-02T00:00:00Z": "Available",
        "2021-01-03T00:00:00Z": "Reserved",
        "2021-01-04T00:00:00Z": "Not Available",
        "2021-01-05T00:00:00Z": "Not Available",
        "2021-01-06T00:00:00Z": "Available",
        "2021-01-07T00:00:00Z": "Not Available",
        "2021-01-08T00:00:00Z": "Not Available",

    },
    "PERMITTEDEQUIPMENT": [
        {"EquipmentName": "Tent", "MaxLength": 10},
        {"EquipmentName": "Spam", "MaxLength": 100},
        {"EquipmentName": "Trailer", "MaxLength": 40},
    ]

}

CAMPSITE_NO_AVAIL = deepcopy(CAMPSITE)
del CAMPSITE_NO_AVAIL['availabilities']

# This list is sorted.
SORTED_CAMPSITES = [
    Campsite({"CampsiteID": 223, "CampsiteType": "lame",
              "Loop": "A", "CampsiteName": "001"}),
    Campsite({"CampsiteID": 133, "CampsiteType": "lame",
              "Loop": "A", "CampsiteName": "002"}),
    Campsite({"CampsiteID": 113, "CampsiteType": "lame",
              "Loop": "A", "CampsiteName": "004"}),
    Campsite({"CampsiteID": 153, "CampsiteType": "lame",
              "Loop": "B", "CampsiteName": "101"}),
    Campsite({"CampsiteID": 213, "CampsiteType": "lame",
              "Loop": "B", "CampsiteName": "102"}),
    Campsite({"CampsiteID": 155, "CampsiteType": "lame",
              "Loop": "C", "CampsiteName": "001"}),
    Campsite({"CampsiteID": 134, "CampsiteType": "lame",
              "Loop": "C", "CampsiteName": "011"}),
    Campsite({"CampsiteID": 625, "CampsiteType": "lame",
              "Loop": "C", "CampsiteName": "021"}),
    Campsite({"CampsiteID": 234, "CampsiteType": "lame",
              "Loop": "C", "CampsiteName": "031"}),
]

for cs in SORTED_CAMPSITES:
    for x in ["PERMITTEDEQUIPMENT", "ATTRIBUTES", "availabilities",
              "FacilityID"]:
        cs[x] = CAMPSITE[x]


class TestCampsite():
    campsite = Campsite(CAMPSITE)

    def test_id(self):
        assert self.campsite.id == 1

    def test_name(self):
        assert self.campsite.name == self.campsite["CampsiteName"]

    def test_site_type(self):
        assert self.campsite.site_type == self.campsite["CampsiteType"]

    def test_loop(self):
        assert self.campsite.loop == self.campsite["Loop"]

    def test_availabilities(self):
        assert self.campsite.availabilities == ['2021-01-01 to 2021-01-02',
                                                '2021-01-06']

    def test_blank_availabilities(self):
        cs = Campsite(CAMPSITE_NO_AVAIL)
        assert cs.availabilities == []

    def test_available_nights(self):
        assert self.campsite.available_nights == 3

    def test_permitted_equipment_lengths(self):
        assert self.campsite.permitted_equipment_lengths == \
            {"Tent": 10,
             "Trailer": 40,
             "Spam": 100}

    def test_supports_equipment(self):
        assert self.campsite.supports_equipment("Spam", 99)
        assert self.campsite.supports_equipment("Spam", 100)
        assert not self.campsite.supports_equipment("Spam", 101)

    def test_site_url(self):
        assert self.campsite.site_url == "https://www.recreation.gov/camping/campsites/1"

    def test_campsite_sorting(self):
        """Sorting is done based on Loop, then Name.
        """

        sites = SORTED_CAMPSITES

        # Randomize it.
        # NOTE: don't use random.shuffle. That's done in-place!!
        shuffled_sites = sample(sites, k=len(sites))

        assert sorted(shuffled_sites) == sites
        # Just to be sure . . . the shuffle actually did something.
        assert shuffled_sites != sites


cset = CampsiteSet.from_list(SORTED_CAMPSITES)
emptycset = CampsiteSet({})


class TestCampsiteSet():
    def test_from_list(self):
        assert isinstance(cset, (CampsiteSet, ))
        assert len(cset) == len(SORTED_CAMPSITES)

    def test_filter_by_equipment(self):
        """Show that filter by equipment works.
        """
        # All the campsites support a 100 foot long spam.
        assert cset.filter_by_equipment("Spam", 100) == cset
        # Asking for a 101 foot long spam yields an empty object.
        assert cset.filter_by_equipment("Spam", 101) == CampsiteSet({})

    def test_exclude_by_campsite_type(self):

        # Excluding all campsites of type lame returns nothing.
        assert cset.exclude_by_campsite_type("lame") == CampsiteSet({})
        # Excluding all campsites of type Spanish Inquisition returns
        # the original.
        assert cset.exclude_by_campsite_type("Spanish Inquisition") == cset

    def test_filter_by_campsite_type(self):

        # Excluding all campsites of type lame returns nothing.
        assert cset.filter_by_campsite_type("lame") == cset
        # Excluding all campsites of type Spanish Inquisition returns
        # the original.
        assert cset.filter_by_campsite_type("Spanish Inquisition") == emptycset

    def test_apply_filters(self):
        assert cset.apply_filters({}) == cset
        assert cset.apply_filters(
            {"exclude_by_campsite_type": {"args": ["lame"]}}) == emptycset
        assert cset.apply_filters(
            {"filter_by_campsite_type": {"args": ["lame"]}}) == cset

    def test_with_availability(self):
        assert cset.with_availability() == cset