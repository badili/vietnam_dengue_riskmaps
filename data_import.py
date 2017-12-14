# A script to insert the json data to a database

import json
from flask_sqlalchemy import SQLAlchemy
from dengue_map import app

db = SQLAlchemy(app)

with open('data/vietnam.json') as geo_json:
    all_geojsons = json.load(geo_json)

    for geojson in all_geojsons.iteritems():
        if geojson[1] == 'FeatureCollection':
            continue

        # insert query
        insert_q = "INSERT INTO provinces(province_id, name1, name2, varname, engtype, type2, isocode, geometry) values('%s','%s','%s','%s','%s','%s','%s','%s')"
        # print len(geojson)
        for feature in geojson[1]:
            # we have geometry, type and properties as keys
            # 2nd level we have: NAME_2, NAME_1, VARNAME_2, ENGTYPE_2, ID_2, TYPE_2, ISOCODE_2
            try:
                res = db.engine.execute(insert_q % (
                    feature['properties']['ID_2'],
                    feature['properties']['NAME_1'],
                    feature['properties']['NAME_2'],
                    feature['properties']['VARNAME_2'],
                    feature['properties']['ENGTYPE_2'],
                    feature['properties']['TYPE_2'],
                    feature['properties']['ISOCODE_2'],
                    json.dumps(feature['geometry'])
                ))
                # print res
            except Exception as e:
                print(str(e))
                exit
        # print geojson[1]
        exit
