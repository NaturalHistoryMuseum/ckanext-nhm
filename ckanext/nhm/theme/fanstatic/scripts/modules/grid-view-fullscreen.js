/**
 * Add a full screen mode on the grid view for supported browsers
 */
this.ckan.module('grid-view-fullscreen', function($, _) {
  var self;

  return {
    initialize: function() {
      self = this;
      var body = $('body').get(0);
      if (body.requestFullscreen || body.mozRequestFullScreen || body.webkitRequestFullscreen /*|| body.msRequestFullscreen*/) {
        self._on_grid_init(function () {
          self._is_full_screen = false;
          self.controls = $('div.controls', self.el);
          self.button = $('<a class="expand"></a>')
            .attr('href', '#')
            .attr('title', 'full screen')
            .html('<i class="fa fa-expand"></i>')
            .appendTo(self.controls)
            .click(self._toggle_fullscreen)
        });
      }
    },

    /**
     * Wait for the grid to be loaded, and call the given callback when done.
     * Note that using an interval is the only reliable and cross browser
     * way to do this.
     */
    _on_grid_init: function(callback){
      if ($('div.controls', this.el).length > 0){
        callback();
      } else {
        setTimeout(function(){
          self._on_grid_init(callback);
        }, 250);
      }
    },

    /**
     * Toggle full screen on/off
     */
    _toggle_fullscreen: function(e){
      var body = $('body').get(0);
      if (self._is_full_screen) {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
        $(body).removeClass('fullscreen');
      } else {
        //FIXME: Handle older browsers
        if (body.requestFullscreen) {
          body.requestFullscreen();
        } else if (body.mozRequestFullScreen) {
          body.mozRequestFullScreen();
        } else if (body.webkitRequestFullscreen) {
          body.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
        } else if (body.msRequestFullscreen) {
          body.msRequestFullscreen();
        }
        $(body).addClass('fullscreen');
      }
      self._is_full_screen = !self._is_full_screen;
      self._resize_slickgrid();
      e.stopPropagation();
      return false;
    },

    /**
     * Resize the grid canvas
     *
     * This uses a delay timer to ensure that the browser has had time to
     * switch before we measure available height.
     */
    _resize_slickgrid: function(){
      var $grid = $('div.recline-slickgrid');
      if ($grid.length > 0 && typeof($grid.get(0).grid) !== 'undefined') {
        setTimeout(function() {
          var grid = $grid.get(0).grid;
          var height = 0;
          if (self._is_full_screen){
            self._base_height = $grid.height();
            height = $(document).height() - $('div.controls').height() - 32;
          } else {
            height = self._base_height;
          }
          console.log(height);
          $grid.height(height);
          grid.resizeCanvas();
        }, 250);
      }
    }
  }
});
