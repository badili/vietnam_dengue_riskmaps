var RVF_DSF = function RVF_DSF(){
    this.polygon_lines = {
        "color": "#ff7800",
        "weight": 1,
        "fill-opacity": 1.3
    };

    this.counties = {
        "color": "#628cff",
        "weight": 0.4,
        "fill-opacity": 1.3
    };
    this.rvf_color = [
        // '#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000'
        '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000', '#ca0000'
    ];

    // a regular expression for formatting the results
    this.reEscape = new RegExp('(\\' + ['/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\'].join('|\\') + ')', 'g');

    this.layersData = [];
}

RVF_DSF.prototype.initiateMap = function(lat, lon, zoom, include_overlay = true){
    if (lat == undefined) {
        rvf_dsf.map = L.map('leaflet_map', rvf_dsf.default_zoom).setView([0.2934628,38.132656], 6);
    }
    else {
        rvf_dsf.map = L.map('leaflet_map', rvf_dsf.default_zoom).setView([lat, lon], zoom);
    }

    if(include_overlay){
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="http://mapbox.com">Mapbox</a>',
            id: 'mapbox.streets',
            detectRetina: false
        }).addTo(rvf_dsf.map);
    }
};

RVF_DSF.prototype.initiateDivisions = function () {
    // load the divisions geojson
    $('#loading_spinner').toggleClass('hidden');
    $.get('/divisions_data', function(response){
        rvf_dsf.layersData = [];
        $.each(response, function(i, that){
            var this_css = rvf_dsf.counties;

            var color_index = Math.ceil(parseFloat(that.risk_factor)*10);
            this_css.color = rvf_dsf.rvf_color[color_index];
            if (color_index > 8){
                console.log(color_index);
            }

            var poly = $.parseJSON(that.polygon);
            var n_layer = L.geoJSON(poly, {style: this_css, c_name: that.c_code}).addTo(rvf_dsf.map);

            n_layer.on('mouseover', function(){
//                setTimeout(function() { rvf_dsf.initiateCountyResultsPopup(that); }, 200);
            });
            n_layer.on({click: function(){
                var risk_factor = undefined, prev_risk_factor = Math.random(0, 1);
                if (that.risk_factor < 0.3){
                    risk_factor = 'Low Risk';
                    rf_style = 'primary';
                }
                else if (that.risk_factor < 0.5){
                    risk_factor = 'Medium Risk';
                    rf_style = 'warning';
                }
                else if (that.risk_factor < 1){
                    risk_factor = 'High Risk';
                    rf_style = 'danger';
                }
                if (prev_risk_factor < 0.3){
                    pv_risk_factor = 'Low Risk';
                    pv_rf_style = 'primary';
                }
                else if (prev_risk_factor < 0.5){
                    pv_risk_factor = 'Medium Risk';
                    pv_rf_style = 'warning';
                }
                else if (prev_risk_factor < 1){
                    pv_risk_factor = 'High Risk';
                    pv_rf_style = 'danger';
                }

                rvf_dsf.displayDivisionInfo(this, false, parseFloat(that.risk_factor).toFixed(2), rf_style);
                $('#map_title').html(sprintf('%s Division, Oct 2017 - Dec 2017', that.district_name, that.division_name));
                $('#division_info').html(sprintf("<span class='label label-%s pull-right'>%s</span><h5 id='division_title'>%s Division Overview</h5>", rf_style, risk_factor, that.division_name));
                $('#risk_mean').text(parseFloat(that.risk_factor).toFixed(2));
                $('#prev_risk_factor').html(sprintf("<span class='text-%s'>%s</span>", pv_rf_style, parseFloat(prev_risk_factor).toFixed(2)));
                $('#risk_factor').html(sprintf("<span class='text-%s'>%s</span>", rf_style, risk_factor));
            }});
        });
        $('#loading_spinner').toggleClass('hidden');
    });
};

RVF_DSF.prototype.displayDivisionInfo = function (division_clicked=undefined, direct_load=false, risk_factor=undefined, rf_style=undefined) {
    // load the division metadata
    // Clear the map and show the division
    // RVF_DSF.prototype.clearLayers();
    // RVF_DSF.prototype.deleteMap();

    if (direct_load == true) {
        // Get the current division id from the URL
        some = new URLSearchParams(window.location.search);
        division_id = some.get('division_id');
        url = window.location.origin+'/view_division?division_id='+division_id+'&risk='+risk_factor
    }
    if (division_clicked != undefined) {
        division_id = division_clicked.options.c_name;
        url = '/view_division?division_id='+division_id+'&risk='+risk_factor
    }
    $.get(url, function(response){
        response_structure = response[0]
        if (direct_load == true) {
            // Initialize the map
            rvf_dsf.initiateMap(response_structure.c_lat, response_structure.c_lon, 10);
        }

        // $('#map_title').html(sprintf('%s Division', response_structure.c_name));
        // After drawing the division, then show it's basic metadata that we have
        $('.risk_count').text(response_structure.risk_count)
        // $('.risk_mean').text(response_structure.risk_mean);
        $('.risk_sum').text(response_structure.risk_sum);
        $('.division_id').text(response_structure.c_name);
        var struct = rvf_dsf.generateAccordion(response_structure.interventions, rf_style);
        $('#interventions').html(struct);
    })
};

RVF_DSF.prototype.generateAccordion = function(data){
    var struct = '', i = 0, action_types = ['primary', 'warning', 'danger'];
    $.each(data, function(key1, val1){
        i++;
        $('#div_state').html(sprintf("<span class='text-%s'>%s interventions</span>", rf_style, key1));
        struct += '<div class="panel panel-default">\n';
        var j = 0;
        $.each(val1, function(key2, val2){
            j++;
            struct += '<div class="panel-heading">\
                        <h1 class="panel-title">\
                            <a data-toggle="collapse" data-parent="#div_'+j+'" href="#div_'+i+j+'">'+key2+'</a>\
                        </h1>\
                    </div>';
            struct += '<div class="panel-collapse collapse" id="div_'+i+j+'">';
            var k = 0;
            $.each(val2, function(key3, val3){
                k++;
                struct += '<div class="panel-heading">\
                            <h3 class="panel-title">\
                                <a data-toggle="collapse" data-parent="#div_'+k+'" href="#div_'+i+j+k+'">'+key3+'</a>\
                            </h3>\
                        </div>';
                struct += '<div id="div_'+i+j+k+'" class="panel-collapse collapse">';
                var l = 0;
                $.each(val3, function(key4, val4){
                    l++;
                    struct += '<div class="panel-heading">\
                                <h4 class="panel-title">\
                                    <a data-toggle="collapse" data-parent="#div_'+i+'" href="#div_'+i+j+k+l+'">'+key4+' Actions</a>\
                                </h4>\
                            </div>';

                    // begin collapse
                    struct += '<div id="div_'+i+j+k+l+'" class="panel-collapse collapse">';
                    // panel body
                    struct += '<div class="panel-body">';
                    
                    // actions
                    struct += '<div class="ibox float-e-margins">\
                                <div class="ibox-content no-padding dark-bg">';

                    struct += '<ul class="list-group">';
                    $.each(val4.human_health, function(i, action){
                        var rand = Math.ceil(Math.random()*(4-1))-1;
                        var cur_act_type = action_types[rand];
                        struct += sprintf('<li class="list-group-item"><span class="label label-%s">%d</span>   %s<span class="badge badge-primary">HH</span></li>', cur_act_type, parseInt(i)+1, action);
                    });

                    $.each(val4.animal_health, function(i, action){
                        var rand = Math.ceil(Math.random()*(4-1))-1;
                        var cur_act_type = action_types[rand];
                        struct += sprintf('<li class="list-group-item"><span class="label label-%s">%d</span>   %s<span class="badge badge-success">AH</span></li>', cur_act_type, parseInt(i)+1, action);
                    });
                    struct += '</ul>';
                    struct += '</div></div>';    // actions

                    // end panel body
                    struct += '</div>';
                    // end collapse
                    struct += '</div>';
                });
                struct += '</div>';
            });
            struct += '</div>';
        });
        struct += '</div>';
    });

    return struct;
};

RVF_DSF.prototype.clearLayers = function () {
    rvf_dsf.map.eachLayer(function (layer) {
        if(layer._latlngs != undefined){
            rvf_dsf.map.removeLayer(layer);
        }
    });
};

RVF_DSF.prototype.deleteMap = function () {
    if(rvf_dsf.map != undefined || rvf_dsf.map != null) {
        rvf_dsf.map.remove();
        rvf_dsf.map = null;
    }
};

RVF_DSF.prototype.getColorIndex = function(y_min, y_max, c_val){
    var step = (y_max - y_min)/10;
    var c_index = Math.ceil((c_val - y_min)/step);
    return c_index;
};

var rvf_dsf = new RVF_DSF();

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
    if(window.location.pathname == '/view_division_map'){
        rvf_dsf.displayDivisionInfo(click=undefined, direct_load=true);
    }
    else{
        rvf_dsf.initiateMap();
    }
    if(window.location.pathname == '/') rvf_dsf.initiateDivisions();
});