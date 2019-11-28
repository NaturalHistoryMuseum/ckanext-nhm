<template>
    <div></div>
</template>

<script>
    import {mapGetters} from 'vuex';
    import * as d3 from 'd3-collection';

    export default {
        name:     'BaseEditor',
        props:    ['comparisonType', 'existingTermId'],
        data:     function () {
            return {
                values: {
                    // different comparison types and query entries go here
                }
            }
        },
        computed: {
            ...mapGetters('filters', ['getFilterById']),
            queryValues() {
                return this.values[this.comparisonType];
            }
        },
        created:  function () {
            this.loadExisting();
        },
        methods:  {
            loadExisting() {
                if (this.existingTermId === undefined) {
                    return;
                }
                let existing      = this.getFilterById(this.existingTermId);

                d3.keys(this.values[this.comparisonType]).forEach((k) => {
                    this.$set(this.values[this.comparisonType], k, existing.content[k] || null);
                });
            }
        },
        watch: {
            values:  {
                handler: function () {
                    this.$emit('set-query-values', this.queryValues)
                },
                deep: true
            }
        }
    }
</script>