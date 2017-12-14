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


class KenyanDivisions():
    def __init__(self):
        print "Initializing"

    def get_all_divisions_data(self):
        """
        Get all the divisions IDs and other meta data to display on the
        frontend.
        :return:
        """
        query = """
            SELECT division_id, riskcount, riskmean, risksum, center_lat, division_name, center_long FROM division
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
            SELECT division_id, riskcount, riskmean, risksum, center_lat, center_long, division_name, district_name, province_name, geometry FROM division
        """
        all_results = db.engine.execute(query)
        to_return = []
        rvf_predictions = self.read_predictions()
        # terminal.tprint(json.dumps(rvf_predictions), 'warn')

        for res in all_results:
            division_id = res.division_id
            center_lat = res.center_lat
            center_long = res.center_long
            try:
                pred = rvf_predictions[division_id]
            except Exception as e:
                terminal.tprint(str(e), 'fail')
                terminal.tprint('\tThe division id "%s" was not found in the prediction' % division_id, 'fail')
                pred = -1

            geometry = json.loads(res.geometry)
            to_return.append({
                'c_name': division_id,
                'c_code': division_id,
                'c_lat': center_lat,
                'c_lon': center_long,
                'division_name': res.division_name,
                'district_name': res.district_name,
                'province_name': res.province_name,
                'polygon': json.dumps(geometry),
                'risk_factor': pred
            })

        return to_return

    def get_division_info(self, division_id, risk_factor):
        """
        Get all the data for the divisions, in order to plot them using the
        front end client
        :return: a Polygon like daa strcut that Leaflet JS can use
        """
        query = """
            SELECT division_id, riskcount, riskmean, risksum, center_lat, center_long FROM division WHERE division_id={}
        """.format(division_id)
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
            division_id = res.division_id
            center_lat = res.center_lat
            center_long = res.center_long
            risk_sum = res.risksum
            risk_count = res.riskcount
            risk_mean = res.riskmean

            to_return.append({
                'c_name': division_id,
                'c_code': division_id,
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
        with open('data/out.csv', mode='r') as infile:
            reader = csv.reader(infile)
            my_predictions = defaultdict(dict)
            for rows in reader:
                if not has_started:
                    has_started = True
                    continue
                my_predictions[int(rows[1])] = rows[2]

        return my_predictions
