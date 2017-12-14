import gzip
import json
from cStringIO import StringIO as IO

from flask import render_template, request

from kenyan_divisions_viz import app
from modules import KenyanDivisions
from terminal_output import Terminal

terminal = Terminal()


@app.route('/')
def index():
    kenya_divisions = KenyanDivisions()
    divisions = kenya_divisions.get_all_divisions_data()
    # divisions = []
    return render_template(
        'main_divisions_page.html',
        map_title='Oct 2017 - Dec 2017',
        divisions=divisions
    )


@app.route('/divisions_data')
def base_divisions_map():
    kenya_divisions = KenyanDivisions()
    all_polygons = kenya_divisions.base_divisions_map()
    response = zip_response(json.dumps(all_polygons))
    return response


@app.route('/view_division')
def view_division():
    division_id = request.args.get('division_id')
    risk = request.args.get('risk')
    kenya_divisions = KenyanDivisions()
    all_polygons = kenya_divisions.get_division_info(division_id, risk)
    response = zip_response(json.dumps(all_polygons))
    return response

@app.route('/view_division_map')
def view_division_map():
    return render_template(
        'division_view.html',
        map_title=' Kenyan Divisions Distribution',
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
