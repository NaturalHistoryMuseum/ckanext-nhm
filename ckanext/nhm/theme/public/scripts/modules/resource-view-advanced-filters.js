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
  var disabledFieldClass = 'disabled-field';

  function initialize() {

    self = this

    var resourceId = self.options.resourceId,
        hiddenFields = self.options.hiddenFields,
        fieldGroups = self.options.fieldGroups,
        filterOptions = self.options.filterOptions,
        fields = self.options.fields;

    var filters = ckan.views.filters.get();

    var $filtersWrapper = $('<div></div>');

    $(this).select2('destroy');

    if ($.isEmptyObject(fieldGroups)) {

        $filtersWrapper.append(_makeFieldFilters(resourceId, fields, filters, hiddenFields))
        // Add selected class, mirroring the class on selected tab
        $filtersWrapper.addClass('selected')

    }else{

        var $tabs = $('<ul />');

        $.each(fieldGroups, function (i, groupFields) {

            var groupID = i.replace(/\s+/g, '-').toLowerCase();

            $tabs.append($('<li >').append($('<a href="#' + groupID + '">' + i + '</a>').on( "click", { group: i }, _toggleTab)))

            var $filters = _makeFieldFilters(resourceId, groupFields, filters, hiddenFields)
            $filtersWrapper.append($('<div name="#' + groupID + '"></div>').append($filters));

        })

        $filtersWrapper.prepend($tabs);
        $filtersWrapper.liteTabs({width: 900});

    }

    $filtersWrapper.append(_makeFieldFilterOptions(filterOptions));

    self.el.append($filtersWrapper);

    var $formActions = $('<div class="form-actions"></div>')

    var $displayAllFieldCheckbox = $('<input type="checkbox" id="display-all-fields" name="display-all-fields" />').click(_toggleDisplayAllFields)
    var $tab = $('div.selected', self.el);

    // Only if all checkboxes are checked, should the checkbox be checked for toggling off all fields
    if ($('input[name^="field_display"]:checked', $tab).length == $('input[name^="field_display"]', $tab).length){
        $displayAllFieldCheckbox.prop('checked', true);
    }

    $formActions.append($('<div class="toggle-all-fields"></div>')
        .append($('<label for="display-all-fields">Display all fields</label>'))
        .append($displayAllFieldCheckbox)
    );

    $formActions.append($('<button class="btn btn-primary save" type="submit"><i class="icon-search"></i><span>Search</span></button>').click(_submitSearch));

    // Add submit button
    self.el.append($formActions)

  }

  function _toggleDisplayAllFields(e){
      /**
       * CLick event handler - toggle show all fields
        * @type {*|jQuery|HTMLElement}
       */

    var checkBoxes = $('input[name^="field_display"]:not(:disabled)', self.el.find('div.selected'));
    checkBoxes.prop("checked", $(this).prop('checked'));
    checkBoxes.trigger('change');

  }

  function _toggleFieldDisplay(){
      /**
       * Toggle display of an individual field
       */

       var $label = $('label[for="' + $(this).prop('name') + '"]');

       if ($(this).is(':checked')){
           $label.removeClass(hiddenFieldClass)
       }else{
           $label.addClass(hiddenFieldClass);
       }

       if($(this).is(':disabled')){
           $label.addClass(disabledFieldClass)
       }else{
           $label.removeClass(disabledFieldClass)
       }

  }

  function _toggleTab(event){

      // Update reset display fields checkbox
      $('.toggle-all-fields label').html('Display all ' + event.data.group.toLowerCase() + ' fields');

      // Reset display all fields checkbox
      var $tab = $('div[name=' + event.currentTarget.hash + ']');

      // Only if all checkboxes are checked, should the checkbox be checked for toggling off all fields
      var checked = $('input[name^="field_display"]:checked', $tab).length == $('input[name^="field_display"]', $tab).length
      $('input#display-all-fields').prop('checked', checked);

  }

  function _makeFieldFilterOptions(filterOptions){

    var $filterOptions = $('<div></div>');

    // Add filter options checkboxes
      for (var name in filterOptions){
        if (!filterOptions.hasOwnProperty(name)){
          continue;
        }
        var checked = filterOptions[name]['checked'] ? 'checked' : '';
        var label = filterOptions[name]['label'];
        $filterOptions.append([
          '<label class="resource-view-filter-option">',
          '<input type="checkbox" value="1" name="filters[' + name + ']"' + checked + ' />',
          '<span>' + label + '</span>',
          '</label>'
        ].join(""));
      }

      return $filterOptions

  }

  function _makeFieldFilters(resourceId, fields, filters, hiddenFields) {
   /**
    * Loop through all the fields, making a filed and appending to the filters div
    */

    var $filtersDiv = $('<div></div>');

    $.each(fields, function (i, field) {

        if(typeof field == 'string'){
            field = {
                name: field,
                label: field
            }
        }


        // We don't show the ID field - cannot be hidden anyway
        if (field.name != '_id') {

            var value

            // Do we a have a filter for this field
            if (filters.hasOwnProperty(field.name)) {
                // We no longer allow multiple OR values
                value = filters[field.name][0]
            }

            $filtersDiv.append(_makeField(field, value, ($.inArray(field.name, hiddenFields) == -1)));
        }

    });

    function _makeField(field, value, displayField) {
    /**
     * Make a field filter, comprising label, select2 auto-lookup
     * list and a checkbox for controlling display of the field - if checked field will be displayed
     * @type {*|jQuery}
     */

     // Build the filter, including a field display checkbox
     var $filter = $('<div class="advanced-filter-field-value"></div>')
         .append($('<input type="hidden" name="filters[' + field.name + ']" />'))

     var $fieldDisplayCheckbox = $('<input class="toggle-field-display" type="checkbox" name="field_display[' + field.name + ']" id="field_display[' + field.name + ']" value="1" />').change(_toggleFieldDisplay)

     // Label to show / hide field
     var $label = $('<label for="field_display[' + field.name + ']"><span class="show" title="Visible"><i class="icon-eye-open" /></span><span class="hide" title="Hidden"><i class="icon-eye-close" /></span></label>');

     // If we have a populated filter value or this is a display field, check the box
     if (displayField || value){
         $fieldDisplayCheckbox.prop('checked', true)
         if (value){
             // If we have a value, this must be disabled and checked
             // User must remove the filter value, to un-check the box
             $fieldDisplayCheckbox.prop('disabled', true)
             $label.addClass(disabledFieldClass);
         }
     }else{
         // On load, add the hidden field label class
         // We will theme the label based on whether or not the field is hidden
         $label.addClass(hiddenFieldClass);
     }

     // Add field display label
     $filter.append($fieldDisplayCheckbox).append($label);

     // Build a field consisting of label and input
     var $field = $('<div class="advanced-filter-field"></div>')
         .append($('<label for="filters[' + field.name + ']">' + field.label + '</label>'))
         .append($filter);

     var queryLimit = 20;

     // Add the select2 lookup list
     $field.find('input[name^="filters"]').select2({
        allowClear: true,
        placeholder: ' ', // select2 needs a placeholder to allow clearing
        width: 142,
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
              fields: field.name,
              distinct: true,
              sort: field.name
            };

            if (term !== '') {
              var q = {};
              q[field.name] = term + ':*';
              query.q = JSON.stringify(q);
            }

            return query;
          },
          results: function (data, page) {
            var records = data.result.records,
                hasMore = (records.length < data.result.total),
                results;

            results = $.map(records, function (record) {
              return { id: record[field.name], text: String(record[field.name]) };
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
        $checkbox.prop('disabled', true);
    }else{
        // We no longer have a value in this filter, so the field isn't automatically selected
        // Enable the field - but do not change the value
        $checkbox.prop('disabled', false);
    }

    // Trigger the change event
    $checkbox.trigger('change');

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

         if ($(this).prop('type') == 'checkbox'){
            if ($(this).prop('checked')){
                ckan.views.filters.set(filterName, 'true');
            }else{
                ckan.views.filters.unset(filterName);
            }
         }else if ($(this).val()){
            ckan.views.filters.set(filterName, $(this).val());
         }else{
            ckan.views.filters.unset(filterName);
         }

     })

  }

  return {
    initialize: initialize,
    options: {
        fields: [],  // List of fields. Required
        hiddenFields: [], // List of fields to hide
        fieldGroups: {},  // Groupings of fields. Optional
        filterOptions: {}  // Extra filter options - has type etc.,
    }
  };
});
