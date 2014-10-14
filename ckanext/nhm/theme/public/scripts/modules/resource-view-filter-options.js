this.ckan.module('resource-view-filter-options', function($, _) {
  var self;

  return {
    options: {
      /* Dict of option id to object defining initial value and label, eg.
       * {'_has_image': {'checked': False, 'label': 'Has image'}}
       */
      'options': {}
    },

    /**
     * Initialize the resource view filter options by setting up option
     * checkboxes and click handlers.
     */
    initialize: function() {
      self = this;

      // Add checkboxes
      for (var name in self.options['options']){
        if (!self.options['options'].hasOwnProperty(name)){
          continue;
        }
        var checked = self.options['options'][name]['checked'] ? 'checked' : '';
        var label = self.options['options'][name]['label'];
        self.el.append([
          '<label class="resource-view-filter-option">',
          '<input type="checkbox" value="1" name="' + name + '" ' + checked + ' />',
          '<span>' + label + '</span>',
          '</label>'
        ].join(""));
      }

      // Add click handler
      $('input[type=checkbox]', self.el).change(self._option_changed)
    },

    /**
     * Event handler called when an option is changed. `this` is set to the
     * option element.
     *
     * @private
     */
    _option_changed: function(){
      var option = this;
      var name = $(option).attr('name');
      var checked = $(option).prop('checked');
      var ckan_url = new window.CkanFilterUrl(window.location.href);
      if (checked){
        ckan_url.add_filter(name, 'true');
      } else {
        ckan_url.remove_filter(name);
      }
      window.location.href = ckan_url.get_url();
    }
  };
});
