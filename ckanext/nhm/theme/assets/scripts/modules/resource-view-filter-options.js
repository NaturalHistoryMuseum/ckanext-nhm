ckan.module('resource-view-filter-options', function ($) {
  var self;

  function initialize() {
    self = this;

    var $filterOptions = $('<div class="filter-options"></div>');

    // Add filter options checkboxes
    for (var name in self.options.filterOptions) {
      if (!self.options.filterOptions.hasOwnProperty(name)) {
        continue;
      }
      var label = self.options.filterOptions[name]['label'];
      var $label = $('<label>')
        .text(label)
        .addClass('resource-view-filter-option');
      var $input = $('<input type="checkbox">')
        .attr({
          value: '1',
          name: name,
          checked: self.options.filterOptions[name]['checked'],
        })
        .change(onChange);

      $input.prependTo($label);
      $label.appendTo($filterOptions);
    }

    self.el.append($filterOptions);
  }

  function onChange(e) {
    var filterField = e.target.name;
    if (e.target.checked) {
      ckan.views.filters.set(filterField, true);
    } else {
      ckan.views.filters.unset(filterField);
    }
  }

  return {
    initialize: initialize,
    options: {
      resourceId: null,
      filterOptions: null,
    },
  };
});
