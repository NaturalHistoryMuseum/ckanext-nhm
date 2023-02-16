/*
 * Similar to bootstrap toggle collapse, but works on select elements
 * If no option is selected (or option evaluates to False/0/None)
 * The target will be hidden
 * If an option is selected, the target will display
 *
 * See resource_form.html for usage
 *
 */
this.ckan.module('toggle-select', function ($, _) {
  var self, $target;
  return {
    options: {
      target: '',
    },

    initialize: function () {
      /* Initialises the module setting up elements and event listeners.
       *
       * Returns nothing.
       */
      self = this;
      $target = $(self.options.target);
      self.el.change(function (e) {
        self._toggleDisplay(e.target.value);
      });

      // Show / Hide on load
      self._toggleDisplay($(self.el).val());
    },

    _toggleDisplay: function (value) {
      /**
       * Toggle display of target element
       */
      if (value && value != 0 && value != 'None') {
        $target.show();
      } else {
        $target.hide();
      }
    },
  };
});
