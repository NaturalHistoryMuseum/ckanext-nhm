// Integrating the NHM Map

this.recline = this.recline || {};
this.recline.View = this.recline.View || {};

(function($, my) {

my.NHMMap = Backbone.View.extend({
  className: 'recline-nhm-map well',
  template: '\
    <div class="recline-map"> \
      <div class="panel map"></div> \
    </div> \
  ',
  initialize: function() {
    this.el = $(this.el);
    _.bindAll(this, 'render');
    this.model.queryState.bind('change', this.render);
  },
  render: function() {

    var self = this;

    out = Mustache.render(this.template);
    $(this.el).html(out);
    this.$map = this.el.find('.panel.map');

//    if (!self.mapReady){
//      self._setupMap();
//    }

    self._setupMap();

    self.redraw();

//    var filters = {}
//
//    $.each(this.model.queryState.attributes.filters, function( i, filter ) {
//        filters[filter.field] = filter.term;
//    });
//
//    if (this.model.queryState.attributes.q){
//        filters['q'] = this.model.queryState.attributes.q
//    }

//    var tmplData = {}
//
//    var jqxhr = $.ajax({
//        url: '/map/' + this.model.id,
//        type: 'POST',
//        data: filters,
//        success: function(response) {
//            tmplData = response;
//        },
//        async: false
//    });
//
//    var out = Mustache.render(this.template, tmplData);
//    var out = Mustache.render(this.template);
//    this.el.html(out);

  },

  show: function() {
     $('.recline-pager').hide();
  },

  hide: function() {
     $('.recline-pager').show();
  },

  _setupMap: function(){

    var dbname = 'nhm_botany';
    var table = 'botany_all';

    this.map = new L.Map(this.$map.get(0));

    this.map.setView(new L.LatLng(51.505, -0.09), 4, true);
    L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpg', { opacity: 0.8 }).addTo(this.map);

    var baseURL = "http://localhost:4444/database/<%= dbname %>/table/<%= table %>/{z}/{x}/{y}";

    this.tilejson = {
            tilejson: '1.0.0',
            scheme: 'xyz',
            tiles: [],
            grids: [],
            formatter: function(options, data) { return data._id + "/" + data.species + "/" + data.scientific_name }
    };

    var url = _.template(baseURL, {dbname: dbname, table: table});
    this.tiles_url = url + '.png';
    this.grids_url = url + '.grid.json?callback={cb}';

    this.info = L.control();
    this.info.options.position = 'bottomright';

    this.info.onAdd = function (map) {
      this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
      this.update();
      return this._div;
    };

    this.info.update = function (props) {
      this._div.innerHTML = "<h4>Botany Records</h4>" + (props ?
      "<b>" + props.data.species + "</b><br />" + props.data._id+"<br />"+ props.data.scientific_name + "<br/>" + props.data.count + " records overlapping"
      : 'Hover over a marker');
    };


    this.mapReady = true;

  },

  redraw: function(){

    var self = this;
    var tile_params = {};
    var grid_params = {};

    var where = [];

    $.each(this.model.queryState.attributes.filters, function( i, filter ) {
        where.push(filter.field + "='" + filter.term + "'");
    });

    if (this.model.queryState.attributes.q){
        where.push("_full_text='" + this.model.queryState.attributes.q + "'");
    }

    tile_params["sql"] = "select * from botany_all";

    if (where.length){
        tile_params["sql"] += " WHERE " + where.join(" AND ");
    }

    where.push('st_intersects(the_geom_webmercator, st_setsrid(!bbox!, 3857))');

    var grid_sql = "SELECT names[1] AS scientific_name, ids[1] as _id, species[1] as species, count, center as the_geom_webmercator" +
      " FROM " +
      "(SELECT array_agg(scientific_name) as names, array_agg(_id) AS ids, array_agg(species) as species, COUNT( geom ) AS count, ST_SnapToGrid( the_geom_webmercator, 1000, 1000) AS center " +
      "FROM botany_all WHERE " +
      where.join(' AND ') +
      " GROUP BY ST_SnapToGrid( the_geom_webmercator, 1000, 1000) " +
      "ORDER BY count DESC ) as sub "

    grid_params["sql"] = grid_sql;

    if ($.isEmptyObject(tile_params)) {
      this.tilejson.tiles = [this.tiles_url];
    } else {
      this.tilejson.tiles = [this.tiles_url + "?" + $.param(tile_params)];
    }

    if ($.isEmptyObject(grid_params)) {
      this.tilejson.grids = [this.grids_url];
    } else {
      this.tilejson.grids = [this.grids_url + "&" + $.param(grid_params)];
    }

    _.each(layers, function(layer){
        this.map.removeLayer(layer)
    });

    _.each(controls, function(control) {
      this.map.removeControl(control)
    });

    var layers = [];
    var controls = [];

    var testMap = L.tileLayer(this.tilejson.tiles[0]).addTo(this.map);
    var utfGrid = new L.UtfGrid(this.tilejson.grids[0], {
      resolution: 4
    });

    utfGrid.on('mouseover', function(e){ self.info.update(e);}).on('mouseout', function(e){ self.info.update();})
    this.map.addLayer(utfGrid);
    this.map.addControl(this.info);

    controls.push(this.info);
    layers.push(utfGrid);
    layers.push(testMap);

  }


});

})(jQuery, recline.View);