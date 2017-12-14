# A script to insert the json data to a database

import json

with open('vietnam.json') as geo_json:
    all_geojsons = json.load(geo_json)

    for geojson in all_geojsons.iteritems():
        if geojson[1] == 'FeatureCollection':
            continue

        # print geojson[1]
        # print geojson[0]
        # print len(geojson)
        # print geojson[1][0]
        for feature in geojson[1]:
            # we have geometry, type and properties as keys
            # 2nd level we have: NAME_2, NAME_1, VARNAME_2, ENGTYPE_2, ID_2, TYPE_2, ISOCODE_2
            print feature['properties']['ISOCODE_2']
        # print geojson[1]
        # exit