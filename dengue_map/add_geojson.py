# import _mysql
import datetime
import sys
import json

from geojson_utils import centroid

reload(sys)
sys.setdefaultencoding('utf-8')

"""
db = _mysql.connect(
    host="localhost",   # your host, usually localhost
    user="root",        # your username
    passwd="admin",     # your password
    db="vietnam_dengue"          # name of the data base
)
"""

# Create the DB cursor
# cur = db.cursor()
now = datetime.datetime.now()


# Read the geojson file
def load_division_data(geo_file_path):
    """
    Read the Kenyan division geojson and populate a DB specified above.
    """
    geo_file = open(geo_file_path, 'r')
    geo_file_dict = json.loads(geo_file.read())

    for i in range(len(geo_file_dict.get('features'))):
        # Read this particular division details
        data_bundle = geo_file_dict.get('features')[i].get('properties')
        province_id = data_bundle.get('ID_2')
        name1 = data_bundle.get('NAME_1')
        name2 = data_bundle.get('NAME_2')
        varname = data_bundle.get('VARNAME_2')
        engtype = data_bundle.get('TYPE_2')
        isocode = data_bundle.get('ISOCODE_2')
        geometry = geo_file_dict.get('features')[i].get('geometry')

        # calculate center_lat and center_long
        try:
            centre_point = centroid(geometry)
            # print "Center Point", centre_point
            # print "*" * 100
            center_lat = centre_point.get('coordinates')[1]
            center_long = centre_point.get('coordinates')[0]
        except TypeError:
            # Means this region has a Multi Polygon not a Polygon
            # So create the centre_points using the largest polygon
            maxx = 0
            for v in geo_file_dict.get('features')[i].get('geometry').get('coordinates'):
              current_length = len(v[0])
              if current_length > maxx:
                  temp_poly = {'type': 'Polygon', 'coordinates': v}
                  maxx = current_length

            centre_point = centroid(temp_poly)

            # print "Center Point for MultiPolygon is", centre_point
            # print "*" * 100
            center_lat = centre_point.get('coordinates')[1]
            center_long = centre_point.get('coordinates')[0]

        query = """
        INSERT into provinces(province_id, name1, name2, varname, engtype, type2, isocode, center_lat, center_long, geometry)
        VALUES("{}",'{}','{}','{}','{}','{}','{}')
        """.format(
            province_id,
            name1,
            name2,
            varname,
            engtype,
            isocode,
            center_lat,
            center_long,
            json.dumps(geometry)
        )

        # Do the inserts
        try:
            print "update provinces set center_lat='%s', center_long='%s' where province_id=%s;" % (center_lat, center_long, province_id)
            # cur.execute(query)
            # print "Added Division {}, to the DB".format(division_id)
        except Exception as e:
            print "ERROR\n\t{}".format(str(e))


if __name__ == "__main__":
    print load_division_data('../data/vietnam.json')
    # db.commit()
