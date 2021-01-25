"""Checks availability at a set of sites I'm interested in staying at.
"""

from recgov.availability import Availability
from recgov._requests import get_session
from os import path, environ
from yaml import load, FullLoader, dump
from pprint import pprint
import requests
from gzip import open as gzopen

BASEDIR=path.dirname(__file__)
APIKEY=environ.get('RECREATION_GOV_KEY')

def main():
    sess = get_session(apikey=APIKEY)

    # Load the config file.
    with open(path.join(BASEDIR, 'config.yml'), 'rb') as fh:
        config = load(fh, Loader=FullLoader)
    # Iterate over each item under "tasks" in the config file.
    assets = [task.get('asset_id') for task in config['tasks']]

    campsite_types = set()
    sites = []

    for asset in assets:
        resp = sess.get_record_iterator(f"https://ridb.recreation.gov/api/v1/facilities/{asset}/campsites")
        sites += [x for x in resp]
        campsite_types = campsite_types.union(set([x['CampsiteType'] for x in sites]))
    with gzopen(path.join(BASEDIR, "cache", f"campsites.yaml.gz"), 'wt') as fh:
        dump(sites, fh)

    print (campsite_types)

# Result: 
# {'TENT ONLY NONELECTRIC', 
# 'STANDARD ELECTRIC', 
# 'GROUP TENT ONLY AREA NONELECTRIC', 
# 'MANAGEMENT', 
# 'RV NONELECTRIC',
# 'WALK TO',
# 'STANDARD NONELECTRIC',
# 'GROUP STANDARD NONELECTRIC'
# }


if __name__ == "__main__":
    main()
