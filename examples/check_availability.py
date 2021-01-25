"""Checks availability at a set of sites I'm interested in staying at.
"""

from recgov.campsites import get_campsites, Campsite, CampsiteSet
from recgov.availability import Availability
from os import path
from yaml import load, FullLoader, dump
from pprint import pprint
from datetime import datetime
import pytz

EST = pytz.timezone("US/Eastern")

BASEDIR=path.dirname(__file__)

def main():

    # Load the config file.
    with open(path.join(BASEDIR, 'config.yml'), 'rb') as fh:
        config = load(fh, Loader=FullLoader)
    # Iterate over each item under "tasks" in the config file.
    for task in config['tasks']:
        task_start = datetime.now(EST)
        print(f"Processing {task['name']}")
        sites = get_campsites(task['asset_id'])
        total_sites = len(sites)
        av = Availability(task['asset_id'])
        # Filter for availability (removes dates outside desired date range)
        filtered_availability = av.apply_filters(task['availability_filters'])

        # av isn't populated until we call apply_filters.
        if len(av) != total_sites:
            raise RuntimeError("Wrong number of sites retrieved by Availability!")

        # Filter sites based on equipment, or site type
        filtered_sites = sites.apply_filters(task['campsite_filters'])
        # Merge the availability data with the sites.
        filtered_sites.ingest_availability(filtered_availability)

    
        task['status'] = {
                'check_completed': datetime.now(EST),
                'duration': (datetime.now(EST) - task_start).total_seconds(),
                'available_campsites': [
                    {'site_id': val.id,
                    'loop': val.loop,
                    'name': val.name,
                    'availabilities': val.availabilities,
                    'link': val.site_url}
                for val in sorted(filtered_sites.with_availability().values())
                ]
            }

    with open(path.join(BASEDIR, 'status.yml'), 'wt') as fh:
        config = dump(config, fh)



if __name__ == "__main__":
    main()
