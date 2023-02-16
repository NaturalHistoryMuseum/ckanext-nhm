/* Table toggle more
 * When a table has more things to it that need to be hidden and then shown more
 */
this.ckan.module('toggle-empty-rows', function ($, _) {
  var self;
  return {
    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      self = this;
      $(
        '<a href="#" class="btn btn-primary"><i class="fas fa-eye-slash" id="toggle-rows-btn"></i>Toggle empty rows</a>',
      )
        .on('click', self._toggleDisplay)
        .insertBefore(self.el);
    },

    _toggleDisplay: function (e) {
      e.preventDefault();
      self.el.toggleClass('table-hide-empty');
      var btn = $('#toggle-rows-btn');
      btn.toggleClass('fa-eye-slash');
      btn.toggleClass('fa-eye');
    },
  };
});
