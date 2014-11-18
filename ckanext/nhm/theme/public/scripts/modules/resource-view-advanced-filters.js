/**
 * This replaces public/base/javascript/modules/resource-view-filters
 *
 * It creates a large form showing all filterable fields, along with
 * Options for turning on/off display of fields
 *
 */

this.ckan.module('resource-view-advanced-filters', function (jQuery, _) {
  'use strict';
  var self;
  function initialize() {

    self = this

    var resourceId = self.options.resourceId,
        fields = self.options.fields,
        $filtersDiv = $('<div></div>');

    var filters = ckan.views.filters.get();

    // Append the filters
    _appendFieldFilters($filtersDiv, resourceId, fields, filters);
    $(this).select2('destroy');
    self.el.append($filtersDiv);

    var $formActions = $('<div class="form-actions"></div>')

    $formActions.append($('<button class="btn btn-primary save" type="submit"><i class="icon-search"></i><span>Search</span></button>').click(_submitSearch));
    $formActions.append($('<label for"display-all-fields">Display all fields</label><input type="checkbox" name="display-all-fields" />').click(_toggleDisplayAllFields))

    // Add submit button
    self.el.append($formActions)

  }

  function _toggleDisplayAllFields(){
    var checkBoxes = $('input[name^="field_display"]:not(:disabled)', self.el);
    checkBoxes.prop("checked", !checkBoxes.prop("checked"));
  }

  function _appendFieldFilters($filtersDiv, resourceId, fields, filters) {
   /**
    * Loop through all the fields, making a filed and appending to the filters div
    */

    var displayFields = filters['_f'] || []

    $.each(fields, function (i, fieldName) {

        var value

        // Do we a have a filter for this field
        if (filters.hasOwnProperty(fieldName)) {
            // We no longer allow multiple OR values
            value = filters[fieldName][0]
        }

        var displayField = ($.inArray(fieldName, displayFields) != -1) || (value !== undefined)

        $filtersDiv.append(_makeField(fieldName, value, displayField));

    });

    function _makeField(fieldName, value, displayField) {
        /**
         * Make a field filter, comprising label, select2 auto-lookup
         * list and a checkbox for controlling display of the field - if checked field will be displayed
         * @type {*|jQuery}
         */

     // Build the filter, including a field display checkbox
     var $filter = $('<div class="advanced-filter-field-value"></div>')
         .append($('<input type="hidden" name="filters['+fieldName+']" />'))

     // Field _id is a required fields; cannot be shown/hidden
     if (fieldName != '_id'){

         var $fieldDisplayCheckbox = $('<input type="checkbox"  name="field_display['+fieldName+']" value="1" />')

         // If we have a populated filter value or this is a display field, check the box
         if (displayField || value){
             $fieldDisplayCheckbox.prop('checked', true)
             if (value){
                 // If we have a value, this must be disabled and checked
                 // User must remove the filter value, to uncheck the box
                 $fieldDisplayCheckbox.prop('disabled', true)
             }
         }

         // Add field display checkbox to the filter
         $filter.append($('<label for="field_display['+fieldName+']">Display field in grid</label>'))
         .append($fieldDisplayCheckbox);
     }

     // Build a field consisting of label and input
     var $field = $('<div class="advanced-filter-field"></div>')
         .append($('<label for="filters['+fieldName+']">' + fieldName + '</label>'))
         .append($filter);

     var queryLimit = 20;

     $field.find('input[name^="filters"]').select2({
        allowClear: true,
        placeholder: ' ', // select2 needs a placeholder to allow clearing
        width: 160,
        minimumInputLength: 0,
        ajax: {
          url: '/api/3/action/datastore_search',
          datatype: 'json',
          quietMillis: 200,
          cache: true,
          data: function (term, page) {
            var offset = (page - 1) * queryLimit, query;

            query = {
              plain: false,
              resource_id: resourceId,
              limit: queryLimit,
              offset: offset,
              fields: fieldName,
              distinct: true,
              sort: fieldName
            };

            if (term !== '') {
              var q = {};
              q[fieldName] = term + ':*';
              query.q = JSON.stringify(q);
            }

            return query;
          },
          results: function (data, page) {
            var records = data.result.records,
                hasMore = (records.length < data.result.total),
                results;

            results = $.map(records, function (record) {
              return { id: record[fieldName], text: String(record[fieldName]) };
            });

            return { results: results, more: hasMore };
          }
        },
        initSelection: function (element, callback) {
          var data = {id: element.val(), text: element.val()};
          callback(data);
        }
      }).on('change', _toggleFieldDisplay).select2("val", value)

      return $field;

    }
  }

  function _toggleFieldDisplay(evt) {
  /**
   * On updating the filter, if we are filtering on the field lock field for display
   * Or if value is removed, unlock the field display
   */
    var name = evt.currentTarget.name.replace('filters', 'field_display')
    var $checkbox = $('input[name="'+ name +'"]', self.el)

    if (evt.val){
        // User has entered a filter for this field - so we want to return the field in the results
        // To let the user know this is happening, automatically select the field, and lock out changes
        $checkbox.prop('checked', true);
        $checkbox.prop('disabled', true);
    }else{
        // We no longer have a value in this filter, so the field isn't automatically selected
        // Enable the field - but do not change the value
        $checkbox.prop('disabled', false);
    }

  }

  function _submitSearch(){
      /**
       * Submit the filter form
       * Loop through all values on the form, adding them to the CKAN view filter object
       */

     var re_filters = new RegExp(/filters\[(.*?)\]/);
     var re_field_display = new RegExp(/field_display\[(.*?)\]/);
     var display_fields = []

     self.el.find('input[name^="field_display"]:checked').each(function(){
        display_fields.push(this.name.match(re_field_display)[1]);
     })

     ckan.views.filters.set('_f', display_fields);

     self.el.find('input[name^="filters"]').each(function(){

         if ($(this).val()){
            var filter_name = this.name.match(re_filters)[1]
            ckan.views.filters.set(filter_name, $(this).val());
         }

     })

  }

  return {
    initialize: initialize,
    options: {}
  };
});
