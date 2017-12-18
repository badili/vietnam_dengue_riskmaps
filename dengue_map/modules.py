import json
import csv
import urllib3
import calendar
import operator

from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict

from dengue_map import app
from terminal_output import Terminal

terminal = Terminal()
db = SQLAlchemy(app)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VietnamDengue():
    def __init__(self):
        print "Initializing"

    def get_all_divisions_data(self):
        """
        Get all the divisions IDs and other meta data to display on the
        frontend.
        :return:
        """
        query = """
            SELECT province_id, center_lat, varname, center_long FROM provinces
        """
        all_results = db.engine.execute(query)
        return all_results

    def base_divisions_map(self, year, month, return_geometry=True):
        """
        Get all the data for the divisions, in order to plot them using the
        front end client
        :return: a Polygon like data strcut that Leaflet JS can use
        """
        query = """
            SELECT province_id, center_lat, center_long, varname, geometry FROM provinces
        """
        all_results = db.engine.execute(query)
        to_return = []
        (rvf_predictions, years, months, high_risk_provinces) = self.read_predictions(year, month)
        # terminal.tprint(json.dumps(rvf_predictions), 'warn')

        for res in all_results:
            province_id = res.province_id
            center_lat = res.center_lat
            center_long = res.center_long
            try:
                pred = rvf_predictions[province_id]
                geometry = json.loads(res.geometry)
                # terminal.tprint(json.dumps(pred), 'fail')
                province = {
                    'province_id': province_id,
                    'c_lat': center_lat,
                    'c_lon': center_long,
                    'varname': res.varname,
                    'risk_factor': "%.5f" % float(pred[year][month]['mean'])
                }
                if return_geometry is True:
                    province['polygon'] = json.dumps(geometry)

                to_return.append(province)
            except Exception as e:
                terminal.tprint(str(e), 'fail')
                terminal.tprint('\tThe division id "%s" was not found in the prediction' % province_id, 'fail')
                pred = -1

        # json.dumps(pred)
        map_title = " Dengue Risk Map for %s, %s" % (calendar.month_name[month], year)
        return {'provinces': to_return, 'months': months, 'years': years, 'high_risk_provinces': high_risk_provinces, 'map_title': map_title}

    def read_predictions(self, cur_year, cur_month):
        """
        Read the predictions received from the model
        """
        has_started = False
        with open('data/data_pred.csv', mode='r') as infile:
            reader = csv.reader(infile)
            my_predictions = defaultdict(dict)
            years = []
            months = []
            high_risk_provinces = {}
            for rows in reader:
                if has_started is False:
                    has_started = True
                    continue
                year = int(rows[3])
                month = int(rows[5])
                if year != cur_year and month != cur_month:
                    continue

                province_name = rows[46]
                province_id = int(rows[47])
                mean = rows[54]
                sd = rows[55]
                low_quant = rows[56]
                mid_quant = rows[57]
                upper_quant = rows[58]

                if year not in years:
                    years.append(year)

                if month not in months:
                    months.append(month)

                # check if the province id is already added
                if province_id not in my_predictions:
                    my_predictions[province_id] = defaultdict(dict)

                # check if the year is already added
                if year not in my_predictions[province_id]:
                    my_predictions[province_id][year] = defaultdict(dict)

                # check if the month is already added
                if month not in my_predictions[province_id][year]:
                    my_predictions[province_id][year][month] = defaultdict(dict)
                else:
                    terminal.tprint('The month %s - %s - %s is repeated' % (province_name, year, month), 'fail')

                # add the data
                my_predictions[province_id]['province_name'] = province_name
                my_predictions[province_id][year][month]['mean'] = mean
                my_predictions[province_id][year][month]['sd'] = sd
                my_predictions[province_id][year][month]['low_quant'] = low_quant
                my_predictions[province_id][year][month]['mid_quant'] = mid_quant
                my_predictions[province_id][year][month]['upper_quant'] = upper_quant
                high_risk_provinces[province_id] = "%.5f" % float(mean)

        # terminal.tprint(json.dumps(my_predictions), 'warn')
        # add the proper month names
        months = sorted(months)
        high_risk_provinces = sorted(high_risk_provinces.items(), key=operator.itemgetter(1), reverse=True)

        all_months = []
        for month in months:
            all_months.append({'index': month, 'name': calendar.month_name[month]})
        return (my_predictions, sorted(years), all_months, high_risk_provinces)
