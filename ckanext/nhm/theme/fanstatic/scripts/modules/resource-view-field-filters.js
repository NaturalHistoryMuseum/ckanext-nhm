/**
 * Created by bens3 on 20/08/2017.
 */
this.ckan.module('resource-view-field-filters', function ($, _) {

    var self;

    function initialize() {
        self = this;

        $('<a title="Filter individual fields" href="#" class="toggle-view-filters">Advanced filters</a>').on('click', toggleFilterDisplay).appendTo(self.el);

        self.$filtersWrapper = $('<div class="resource-view-filters-wrapper" />');

        var fields = self.options.fields,
            fieldGroups = self.options.fieldGroups;
        self.$select = ($('<select name="field" />'));

        // If we have field groups, separate the field select into option groups
        // Otherwise, just provide a long list of fields
        if(fieldGroups.length){
            for (var group in fieldGroups) {
                if (!fieldGroups.hasOwnProperty(group)) continue;
                var $optGroup = $('<optgroup />', {label: group});
                $.each(fieldGroups[group], function(fieldName, fieldLabel ) {
                    if(fields.indexOf(fieldName) !== -1){
                        $optGroup.append($('<option>', {value: fieldName}).text(fieldLabel));
                    }
                });
                self.$select.append($optGroup)
            }
        }else{
            $.each(fields, function (i, fieldName) {
                self.$select.append($('<option>', {value: fieldName}).text(fieldName));
            });
        }
        self.$filtersWrapper.append(self.$select);
        var $input = ($('<input type="text" name="value" />'));
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
                hideFilterDisplay()
            }
        });

        $(document).keyup(function (e) {
            // esc
            if (e.keyCode == 27) {
                hideFilterDisplay()
            }
        });

    }

    function toggleFilterDisplay() {
        self.el.toggleClass('display-filter');
        return false;
    }

    function hideFilterDisplay() {
        self.el.removeClass('display-filter');
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
        var filterName = $select.val(),
            queryLimit = 20;

        var searchParams = ckan.views.filters._searchParams;

        $input.select2({
            width: 'resolve',
            minimumInputLength: 0,
            allowClear: true,
            ajax: {
                url: '/api/3/action/datastore_search',
                datatype: 'json',
                quietMillis: 200,
                cache: true,
                data: function (term, page) {
                    var offset = (page - 1) * queryLimit,
                        query;

                    query = {
                        plain: false,
                        resource_id: resourceId,
                        limit: queryLimit,
                        offset: offset,
                        fields: filterName,
                        distinct: true,
                        sort: filterName
                    };

                    // filter based on the entered term
                    if (term) {
                        var q = {};
                        q[filterName] = term + ":*";
                        query.q = JSON.stringify(q);
                    }
                    if(searchParams['filters']){
                        query.filters = JSON.stringify(searchParams['filters']);
                    }

                    return query;
                },
                results: function (data, page) {

                    var records = data.result.records,
                        hasMore = (records.length < data.result.total),
                        results;

                    results = $.map(records, function (record) {
                        if (record[filterName]) {
                            return {id: record[filterName], text: String(record[filterName])};
                        }
                    });
                    return {results: results, more: hasMore};
                },
            },
            initSelection: function (element, callback) {
                var data = {id: element.val(), text: element.val()};
                callback(data);
            },
        });
    }


    return {
        initialize: initialize,
        options: {
            resourceId: null,
            fields: null,
            fieldGroups: null
        }
    };
});
