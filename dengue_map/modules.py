import json
import csv

import urllib3
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

    def base_divisions_map(self):
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
        rvf_predictions = self.read_predictions()
        # terminal.tprint(json.dumps(rvf_predictions), 'warn')

        for res in all_results:
            province_id = res.province_id
            center_lat = res.center_lat
            center_long = res.center_long
            try:
                pred = rvf_predictions[province_id]
            except Exception as e:
                terminal.tprint(str(e), 'fail')
                terminal.tprint('\tThe division id "%s" was not found in the prediction' % province_id, 'fail')
                pred = -1

            geometry = json.loads(res.geometry)
            # terminal.tprint(json.dumps(pred), 'fail')
            to_return.append({
                'c_name': province_id,
                'c_code': province_id,
                'c_lat': center_lat,
                'c_lon': center_long,
                'varname': res.varname,
                'polygon': json.dumps(geometry),
                'risk_factor': pred[2003][1]['mean']
            })

        return to_return

    def get_division_info(self, province_id, risk_factor):
        """
        Get all the data for the divisions, in order to plot them using the
        front end client
        :return: a Polygon like daa strcut that Leaflet JS can use
        """
        query = """
            SELECT province_id, center_lat, center_long FROM division WHERE province_id={}
        """.format(province_id)
        all_results = db.engine.execute(query)

        all_interventions = defaultdict(dict)

        interventions_q = """
            SELECT id, period_name, sub_period FROM periods where lower_risk_band <= {} AND upper_risk_band >= {}
        """.format(risk_factor, risk_factor)
        interventions = db.engine.execute(interventions_q)

        for intv in interventions:
            if intv.period_name not in all_interventions:
                all_interventions[intv.period_name] = defaultdict()
            cur_sub_period = intv.sub_period

            # initiate the dict for this sub period
            all_interventions[intv.period_name][str(intv.sub_period)] = defaultdict(dict)

            # get the categories
            categories_q = """
                SELECT id, category_name FROM categories where period_id = {}
            """.format(intv.id)
            categories = db.engine.execute(categories_q)

            for cat in categories:
                all_interventions[str(intv.period_name)][str(cur_sub_period)][str(cat.category_name)] = defaultdict(dict)
                # get the activities
                activities_q = """
                    SELECT id, activity_name FROM activities where category_id = {}
                """.format(cat.id)
                activities = db.engine.execute(activities_q)

                for activity in activities:
                    all_interventions[str(intv.period_name)][str(cur_sub_period)][str(cat.category_name)][str(activity.activity_name)] = defaultdict(dict)
                    # get the actions
                    actions_q = """
                        SELECT id, action_type, action FROM actions_to_take where activity_id = {}
                    """.format(activity.id)
                    actions = db.engine.execute(actions_q)

                    for action in actions:
                        if action.action_type not in all_interventions[str(intv.period_name)][str(cur_sub_period)][str(cat.category_name)][str(activity.activity_name)]:
                            all_interventions[str(intv.period_name)][str(cur_sub_period)][str(cat.category_name)][str(activity.activity_name)][action.action_type] = []

                        all_interventions[str(intv.period_name)][str(cur_sub_period)][str(cat.category_name)][str(activity.activity_name)][action.action_type].append(action.action)

        to_return = []
        for res in all_results:
            province_id = res.province_id
            center_lat = res.center_lat
            center_long = res.center_long
            risk_sum = res.risksum
            risk_count = res.riskcount
            risk_mean = res.riskmean

            to_return.append({
                'c_name': province_id,
                'c_code': province_id,
                'risk_sum': risk_sum,
                'risk_mean': risk_mean,
                'risk_count': risk_count,
                'c_lat': center_lat,
                'c_lon': center_long,
                'interventions': all_interventions
            })

        return to_return

    def read_predictions(self):
        """
        Read the predictions received from the model
        """
        has_started = False
        with open('data/data_pred.csv', mode='r') as infile:
            reader = csv.reader(infile)
            my_predictions = defaultdict(dict)
            for rows in reader:
                if has_started is False:
                    has_started = True
                    continue
                province_name = rows[46]
                province_id = int(rows[47])
                year = int(rows[3])
                month = int(rows[5])
                mean = rows[54]
                sd = rows[55]
                low_quant = rows[56]
                mid_quant = rows[57]
                upper_quant = rows[58]

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

        # terminal.tprint(json.dumps(my_predictions), 'warn')
        return my_predictions
