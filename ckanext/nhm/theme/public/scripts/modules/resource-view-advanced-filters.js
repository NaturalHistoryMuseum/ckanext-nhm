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
  var hiddenFieldClass = 'hidden-field';

  function initialize() {

    self = this

    var resourceId = self.options.resourceId,
        hiddenFields = self.options.hiddenFields,
        fieldGroups = self.options.fieldGroups,
        fields = self.options.fields;

    var filters = ckan.views.filters.get();

    var $filtersWrapper = $('<div></div>');

    $(this).select2('destroy');

    if ($.isEmptyObject(fieldGroups)) {

        $filtersWrapper.append(_makeFieldFilters(resourceId, fields, filters, hiddenFields))

    }else{

        var $tabs = $('<ul />');

        $.each(fieldGroups, function (i, groupFields) {

            var groupID = i.replace(/\s+/g, '-').toLowerCase();

            $tabs.append($('<li >').append($('<a href="#' + groupID + '">' + i + '</a>')))

            var $filters = _makeFieldFilters(resourceId, groupFields, filters, hiddenFields)
            $filtersWrapper.append($('<div name="#' + groupID + '"></div>').append($filters));

        })

        $filtersWrapper.prepend($tabs);
        $filtersWrapper.liteTabs({width: 900});

    }

    self.el.append($filtersWrapper);

    var $formActions = $('<div class="form-actions"></div>')

//    var $displayAllFieldCheckbox = $('<input type="checkbox" name="display-all-fields" />').click(_toggleDisplayAllFields)
//
//    // Only if all checkboxes are checked, should the checkbox be checked for toggling off all fields
//    if ($('input[name^="field_display"]:checked', self.el).length == $('input[name^="field_display"]', self.el).length){
//        $displayAllFieldCheckbox.prop('checked', true);
//    }
//
//    $formActions.append($('<div class="toggle-all-fields"></div>')
//        .append($('<label for"display-all-fields">Display all fields</label>'))
//        .append($displayAllFieldCheckbox)
//    );

    $formActions.append($('<button class="btn btn-primary save" type="submit"><i class="icon-search"></i><span>Search</span></button>').click(_submitSearch));

    // Add submit button
    self.el.append($formActions)

  }

  function _toggleDisplayAllFields(e){
      /**
       * CLick event handler - toggle show all fields
        * @type {*|jQuery|HTMLElement}
       */

    var checkBoxes = $('input[name^="field_display"]:not(:disabled)', self.el);
    checkBoxes.prop("checked", $(this).prop('checked'));

  }

  function _toggleFieldDisplay(){
      /**
       * Toggle display of an individual field
       */

       var $label = $('label[for="' + $(this).prop('name') + '"]')

       if ($(this).is(':checked') &! $(this).is(':disabled')){
            $label.removeClass(hiddenFieldClass);
       }else{
            $label.addClass(hiddenFieldClass)
       }

  }

  function _makeFieldFilters(resourceId, fields, filters, hiddenFields) {
   /**
    * Loop through all the fields, making a filed and appending to the filters div
    */

    var $filtersDiv = $('<div></div>');

    $.each(fields, function (i, fieldName) {

        // We don't show the ID field - cannot be hidden anyway
        if (fieldName != '_id') {

            var value

            // Do we a have a filter for this field
            if (filters.hasOwnProperty(fieldName)) {
                // We no longer allow multiple OR values
                value = filters[fieldName][0]
            }

            $filtersDiv.append(_makeField(fieldName, value, ($.inArray(fieldName, hiddenFields) == -1)));
        }

    });

    function _makeField(fieldName, value, displayField) {
    /**
     * Make a field filter, comprising label, select2 auto-lookup
     * list and a checkbox for controlling display of the field - if checked field will be displayed
     * @type {*|jQuery}
     */

     // Build the filter, including a field display checkbox
     var $filter = $('<div class="advanced-filter-field-value"></div>');

     var $fieldDisplayCheckbox = $('<input title="Show/hide field '+ fieldName +' in grid" class="toggle-field-display" type="checkbox" name="field_display['+fieldName+']" value="1" />');

     // Label to show / hide field
//     var $label = $('<label for="field_display['+fieldName+']"><i class="icon icon-eye-open show"></i><i class="icon icon-eye-close hide"></i></label>');

     // If we have a populated filter value or this is a display field, check the box
     if (displayField || value){
         $fieldDisplayCheckbox.prop('checked', true)
         if (value){
             // If we have a value, this must be disabled and checked
             // User must remove the filter value, to uncheck the box
             $fieldDisplayCheckbox.prop('disabled', true)
         }
     }

     // Add field display label
     $filter.append($fieldDisplayCheckbox).append($('<input type="hidden" name="filters['+fieldName+']" />'));

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
      }).on('change', _onChange).select2("val", value)

      return $field;

    }

    return $filtersDiv

  }

  function _onChange(evt) {
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
        // Trigger the change event
        $checkbox.trigger('change');
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

         var filterName = this.name.match(re_filters)[1]

         if ($(this).val()){
            ckan.views.filters.set(filterName, $(this).val());
         }else{
             ckan.views.filters.unset(filterName);
         }

     })

  }

  return {
    initialize: initialize,
    options: {
        fieldGroups: undefined
    }
  };
});
