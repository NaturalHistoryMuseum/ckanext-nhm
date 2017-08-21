/**
 * Created by bens3 on 20/08/2017.
 */
this.ckan.module('resource-view-field-filters', function ($, _) {

    var self;

    function initialize() {
        self = this;

        var fields = self.options.fields;
        self.$select = ($('<select name="field" />'));
        $.each(fields, function (i, field_name) {
            self.$select.append($('<option>', {value: field_name}).text(field_name));
        });
        self.el.append(self.$select);
        var $input = ($('<input type="text" name="value" />'));
        self.el.append($input);


        self.$select.on('change', function () {
            clearDropdown($input);
            applyDropdown($input, self.$select, '05ff2255-c38a-40c9-b657-4ccb55ab2feb')
        });
        applyDropdown($input, self.$select, '05ff2255-c38a-40c9-b657-4ccb55ab2feb')

        $input.on('select2-selecting', onSelect);

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

                    if (term !== '') {
                        var q = {};
                        q[filterName] = term + ':*';
                        query.q = JSON.stringify(q);
                    }

                    return query;
                },
                results: function (data, page) {

                    var records = data.result.records,
                        hasMore = (records.length < data.result.total),
                        results;

                    results = $.map(records, function (record) {
                        if(record[filterName]){
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
            fields: null
        }
    };
});
