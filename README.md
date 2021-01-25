# Status


# recgov
Python modules to interface with [recreation.gov] in order to find suitable availability.

## Usage:

In order to use this library, you'll need to [sign up](https://ridb.recreation.gov/) for 
an api account.  Enabling developer access is under your account settings page.  
You can either store the API KEY in your environment variables as `RECREATION_GOV_KEY`
or you can pass it to your `_session.get_session` calls (much trickier -- not really 
supported).

To install from the checked out code:
``` bash
pip install .
```

To make a link in python to the current code-base:
```bash
pip install --editable .
```

# Generalizing the script:

[recreation.gov](https://www.recreation.gov/) works a little different.  It has a
promising [documented API](https://www.recreation.gov/use-our-data) that provides 
access to campground details, but it doesn't seem to include any availability data.

Common fields used across the api:
| Field Name        | Description                                       |
|-------------------|---------------------------------------------------|
| asset_id          | The campground overall                            |
| name              | Campsite name (often a number)                    |
| org_name          | Who owns the campsite                             |
| loop              | The loop where you can find the site              |

The most promising undocumented endpoint is here: 

* [Month](https://www.recreation.gov/api/camps/availability/campground/234059/month?start_date=2021-02-01T00%3A00%3A00.000Z)
  * Gets availability for an entire month.

The response object looks something like this:
``` json
{
 "availabilities": {
  "2021-03-01T00:00:00Z": "Available",
  // . . . . 
  "2021-03-05T00:00:00Z": "Reserved",
  // . . . . 
  "2021-03-12T00:00:00Z": "Not Available",
  // . . . . 
  "2021-03-31T00:00:00Z": "Reserved"
 },
 "campsite_id": "7859",
 "campsite_reserve_type": "Site-Specific",
 "campsite_type": "GROUP TENT ONLY AREA NONELECTRIC",
 "capacity_rating": "Single",
 "loop": "DEVILS GARDEN CAMPGROUND",
 "max_num_people": 55,
 "min_num_people": 11,
 "quantities": null,
 "site": "JUNIPER BASIN",
 "type_of_use": "Overnight"
}
```