/**
 * Created by bens3 on 29/07/2014.
 */

this.ckan.module('resource-view-filters-ui', function($, _) {

  var self;

  return {

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      self = this;
      $('<a href="#" class="toggle-view-filters">Advanced filters</a>').on('click', this._toggleDisplay).appendTo(self.el);

      $('body').click(function(e){
          if($(e.target).closest('.resource-view-filters-wrapper').length === 0){
            self.hide();
          }
      });

        $(document).keyup(function(e) {
          // esc
          if (e.keyCode == 27) {
              self.hide();
          }

        });
    },

    /* Toggle display of filters (by adding / removing class)
     *
     * Returns false.
     */
    _toggleDisplay: function(e) {
      e.preventDefault();
      self.el.toggleClass('display-filter');
      return false;
    },

    hide: function(){
        self.el.removeClass('display-filter');
    }

  }
});


