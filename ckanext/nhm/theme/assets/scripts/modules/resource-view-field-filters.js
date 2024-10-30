/**
 * Created by bens3 on 20/08/2017.
 */
this.ckan.module('resource-view-field-filters', function ($, _) {
  var self;

  function initialize() {
    self = this;

    $(
      '<a title="Filter individual fields" href="#" class="toggle-view-filters">Advanced filters</a>',
    )
      .on('click', toggleFilterDisplay)
      .appendTo(self.el);

    self.$filtersWrapper = $('<div class="resource-view-filters-wrapper" />');

    var fields = self.options.fields,
      fieldGroups = self.options.fieldGroups;
    self.$select = $(
      '<select aria-label="Select a field to filter" name="field" />',
    );

    // If we have field groups, separate the field select into option groups
    // Otherwise, just provide a long list of fields
    if (fieldGroups.length) {
      for (var group in fieldGroups) {
        if (!fieldGroups.hasOwnProperty(group)) continue;
        var $optGroup = $('<optgroup />', { label: group });
        $.each(fieldGroups[group], function (fieldName, fieldLabel) {
          if (fields.indexOf(fieldName) !== -1) {
            $optGroup.append(
              $('<option>', { value: fieldName }).text(fieldLabel),
            );
          }
        });
        self.$select.append($optGroup);
      }
    } else {
      $.each(fields, function (i, fieldName) {
        self.$select.append(
          $('<option>', { value: fieldName }).text(fieldName),
        );
      });
    }
    self.$filtersWrapper.append(self.$select);
    var $input = $(
      '<input aria-label="Enter a filter value" type="text" name="value" />',
    );
    self.$filtersWrapper.append($input);
    self.el.append(self.$filtersWrapper);

    self.$select.on('change', function () {
      clearDropdown($input);
      applyDropdown($input, self.$select, self.options.resourceId);
    });
    applyDropdown($input, self.$select, self.options.resourceId);

    $input.on('select2-selecting', onSelect);

    // Allow hide on esc / clicking elsewhere on the page
    $('body').click(function (e) {
      if ($(e.target).closest('.resource-view-filters-wrapper').length === 0) {
        hideFilterDisplay();
      }
    });

    $(document).keyup(function (e) {
      // esc
      if (e.keyCode == 27) {
        hideFilterDisplay();
      }
    });
  }

  function toggleFilterDisplay() {
    self.el.toggleClass('display-filter');
    return false;
  }

  function hideFilterDisplay() {
    // self.el.removeClass('display-filter');
  }

  function clearDropdown($input) {
    $input.val(null).trigger('change.select2');
  }

  function onSelect(e) {
    var filterField = self.$select.val(),
      filterValue = e.val;
    ckan.views.filters.set(filterField, filterValue);
  }

  function applyDropdown($input, $select, resourceId) {
    var filterName = $select.val();
    var searchParams = ckan.views.filters._searchParams;

    $input.select2({
      width: 'resolve',
      minimumInputLength: 0,
      allowClear: true,
      ajax: {
        url: '/api/3/action/datastore_autocomplete',
        datatype: 'json',
        quietMillis: 200,
        cache: true,
        data: function (term, page) {
          if (page === 1) {
            // because we're using searchAfter instead of offsets to page through the
            // results we need to keep a track of the after from the previous result.
            // When a new search starts the page is always 1 so when this happens we can
            // clear out the nextAfter value
            self.nextAfter = false;
          }
          const query = {
            resource_id: resourceId,
            limit: 20,
            field: filterName,
            term: term,
          };
          if (searchParams['filters']) {
            // if we don't stringify the filters object they aren't passed through
            // correctly
            query.filters = JSON.stringify(searchParams['filters']);
          }
          if (self.nextAfter) {
            query['after'] = self.nextAfter;
          }
          return query;
        },
        results: function (data, page) {
          if ('after' in data.result) {
            // if there is an after value, store it for the next page query
            self.nextAfter = data.result['after'];
          }
          const results = $.map(data.result.values, function (value) {
            return { id: value, text: String(value) };
          });
          return { results: results, more: 'after' in data.result };
        },
      },
      initSelection: function (element, callback) {
        var data = { id: element.val(), text: element.val() };
        callback(data);
      },
    });
  }

  return {
    initialize: initialize,
    options: {
      resourceId: null,
      fields: null,
      fieldGroups: null,
    },
  };
});
