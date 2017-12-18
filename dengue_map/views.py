import gzip
import json
from cStringIO import StringIO as IO

from flask import render_template, request

from dengue_map import app
from modules import VietnamDengue
from terminal_output import Terminal

terminal = Terminal()


@app.route('/')
def index():
    d_map = VietnamDengue()
    (pred, years, months, high_risk_provinces) = d_map.read_predictions(2012, 12)
    return render_template(
        'provinces_view.html',
        years=years,
        months=months,
        map_title=' Dengue Risk Map for December, 2012',
    )


@app.route('/divisions_data')
def base_divisions_map():
    d_map = VietnamDengue()
    all_polygons = d_map.base_divisions_map(2012, 1)
    response = zip_response(json.dumps(all_polygons))
    return response


@app.route('/get_updated_risk_values')
def get_updated_risk_values():
    year = request.args.get('year')
    month = request.args.get('month')
    d_map = VietnamDengue()
    risk_means = d_map.base_divisions_map(int(year), int(month), False)

    response = app.response_class(
        response=json.dumps(risk_means),
        status=200,
        mimetype='application/json'
    )

    response.data = json.dumps(risk_means)
    response.headers['Content-Encoding'] = 'application/json'
    response.headers['Vary'] = 'Accept-Encoding'
    response.headers['Content-Length'] = len(response.data)

    return response


@app.route('/view_province_map')
def view_province_map():
    d_map = VietnamDengue()
    (pred, years, months) = d_map.read_predictions()
    return render_template(
        'provinces_view.html',
        years=years,
        months=months,
        map_title=' Dengue Risk Map for Dec 2012',
    )


def zip_response(json_data):
    gzip_buffer = IO()
    gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
    gzip_file.write(json_data)
    gzip_file.close()

    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )

    response.data = gzip_buffer.getvalue()
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Vary'] = 'Accept-Encoding'
    response.headers['Content-Length'] = len(response.data)

    return response
