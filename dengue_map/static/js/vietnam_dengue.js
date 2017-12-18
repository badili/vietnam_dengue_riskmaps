var Dengue = function Dengue(){
    this.polygon_lines = {
        "color": "#ff7800",
        "weight": 0.5,
        "fill-opacity": 1.3
    };

    this.counties = {
        "color": "#628cff",
        "weight": 0.8,
        "fill-opacity": 1.3
    };
    this.rvf_color = [
        // '#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000'
        // '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000', '#ca0000'
        "#FFFFCC", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"
    ];

    // a regular expression for formatting the results
    this.reEscape = new RegExp('(\\' + ['/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\'].join('|\\') + ')', 'g');

    this.layersData = [];

    $(document).on('click', '#update_map', this.updateMap);

    // the structure of the popup that we are to create
    this.province_popup = "\
        <div id='chart_popup' class='chart_popup ibox'>\
            <div>\
                <h5><a href='#'>%s </a></h5>\
            </div>\
            <div class='ibox-content'>\
                <h4>Risk Factor: <strong>%s</strong></h4>\
            </div>\
        </div>";
}

Dengue.prototype.initiateMap = function(lat, lon, zoom, include_overlay = true){
    mapboxgl.accessToken = 'pk.eyJ1Ijoic29sb2luY2MiLCJhIjoiY2piNmF5bTAyM2hsdjMzcWt1MTBtNnhpMCJ9.Xr-HLkYndPlgbyCxktmwEw';
    if (lat == undefined) {
        viet_dengue.map = L.map('leaflet_map', viet_dengue.default_zoom).setView([16.982456,106.890051], 5.5);
    }
    else {
        viet_dengue.map = L.map('leaflet_map', viet_dengue.default_zoom).setView([lat, lon], zoom);
    }

    if(include_overlay){
        var CartoDB_Position = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(viet_dengue.map);
    }
};

Dengue.prototype.initiateDivisions = function () {
    // load the divisions geojson
    $('#loading_spinner').toggleClass('hidden');
    viet_dengue.polygons = {};

    $.get('/divisions_data', function(response){
        viet_dengue.layersData = [];
        $.each(response.provinces, function(i, that){
            var this_css = viet_dengue.counties;

            var color_index = Math.ceil(parseFloat(that.risk_factor)*10);
            this_css.color = viet_dengue.rvf_color[color_index];
            if (color_index > 8){
                // console.log(color_index);
                this_css.color = viet_dengue.rvf_color[8];
            }

            var poly = $.parseJSON(that.polygon);
            viet_dengue.polygons[that.province_id] = {'poly': poly, 'prov_name': that.varname};
            var n_layer = L.geoJSON(poly, {style: this_css, province_id: that.province_id}).addTo(viet_dengue.map);

            n_layer.on('mouseover', function(){
               setTimeout(function() { viet_dengue.initiateProvincePopup(that); }, 200);
            });
        });
        viet_dengue.showRiskInfo(response.high_risk_provinces);
        $('#loading_spinner').toggleClass('hidden');
    });
};

Dengue.prototype.initiateProvincePopup = function(that){
    var province_res_html = '';

    var popup = L.popup({autoPan: false})
        .setLatLng([that.c_lat, that.c_lon])    //(assuming e.latlng returns the coordinates of the event)
        .setContent(sprintf(viet_dengue.province_popup, that.varname, that.risk_factor, province_res_html))
        .openOn(viet_dengue.map);
};

Dengue.prototype.updateMap = function(){
    // get the selected year and month
    var cur_year = $('[name=year]').val(), cur_month = $('[name=month]').val();
    if (cur_year == -1){
        alert('Please select a year');
        return;
    }
    if (cur_month == -1){
        alert('Please select a month');
        return;
    }

    $('#loading_spinner').toggleClass('hidden');
    $.get(sprintf('/get_updated_risk_values?year=%s&month=%s', cur_year, cur_month), function(response){
        console.log(response);
        viet_dengue.clearLayers();
        $.each(response.provinces, function(i, that){
            var this_css = viet_dengue.counties;

            var color_index = Math.ceil(parseFloat(that.risk_factor)*10);
            this_css.color = viet_dengue.rvf_color[color_index];
            if (color_index > 8){
                this_css.color = viet_dengue.rvf_color[8];
            }

            var poly = viet_dengue.polygons[that.province_id]['poly'];
            var n_layer = L.geoJSON(poly, {style: this_css, province_id: that.province_id}).addTo(viet_dengue.map);

            n_layer.on('mouseover', function(){
               setTimeout(function() { viet_dengue.initiateProvincePopup(that); }, 200);
            });
        });
        $('#map_title').html(response.map_title);
        viet_dengue.showRiskInfo(response.high_risk_provinces);
        $('#loading_spinner').toggleClass('hidden');
    });
};

Dengue.prototype.clearLayers = function () {
    viet_dengue.map.eachLayer(function (layer) {
        if(layer._latlngs != undefined){
            viet_dengue.map.removeLayer(layer);
        }
    });
};

Dengue.prototype.showRiskInfo = function (data) {
    // show the top provinces with the highest risk
    var risk_factors = '';
    $.each(data, function(i, that){
        risk_factors += sprintf("<tr><td>%d</td><td>%s</td><td>%f</td></tr>", i+1, viet_dengue.polygons[that[0]]['prov_name'], that[1]);
        if(i > 18){
            return false;
        }
    });
    $('#top_provinces tbody').html(risk_factors);
};

Dengue.prototype.deleteMap = function () {
    if(viet_dengue.map != undefined || viet_dengue.map != null) {
        viet_dengue.map.remove();
        viet_dengue.map = null;
    }
};

Dengue.prototype.getColorIndex = function(y_min, y_max, c_val){
    var step = (y_max - y_min)/10;
    var c_index = Math.ceil((c_val - y_min)/step);
    return c_index;
};

var viet_dengue = new Dengue();

$(document).ready(function(){

    $('[data-toggle="tooltip"]').tooltip(); 
    if(window.location.pathname == '/view_division_map'){
        viet_dengue.displayDivisionInfo(click=undefined, direct_load=true);
    }
    else{
        viet_dengue.initiateMap();
    }
    if(window.location.pathname == '/') viet_dengue.initiateDivisions();
});