// Integrating the NHM Map

this.recline = this.recline || {};
this.recline.View = this.recline.View || {};

(function($, my) {

my.NHMMap = Backbone.View.extend({
  className: 'recline-nhm-map well',
  template: '<div>{{& html}}</div>',
  initialize: function() {
    this.el = $(this.el);
    _.bindAll(this, 'render');
    this.model.queryState.bind('change', this.render);
  },
  render: function() {

    var self = this;
    var filters = {}

    $.each(this.model.queryState.attributes.filters, function( i, filter ) {
        filters[filter.field] = filter.term;
    });

    if (this.model.queryState.attributes.q){
        filters['q'] = this.model.queryState.attributes.q
    }

    tmplData = {}

    var jqxhr = $.ajax({
        url: '/map/' + this.model.id,
        type: 'POST',
        data: filters,
        success: function(response) {
            tmplData = response;
        },
        async: false
    });

    var out = Mustache.render(this.template, tmplData);
    this.el.html(out);

  },

  show: function() {
    // TODO: Disable pager
  }

});

})(jQuery, recline.View);