<template>
    <div class="flex-container flex-center">
        <span v-if="comparisonType === 'range'">
            <input type="number" v-model="values.range.greater_than">
            <input type="checkbox" v-model="values.range.greater_than_inclusive" id="greaterThanEq">
            <label for="greaterThanEq" v-if="comparisonType === 'range'">
                <i :class="['fas', 'fa-less-than' + (values.range.greater_than_inclusive ? '-equal' : '')]"></i>
            </label>
        </span>
        <span class="fields">
            field
        </span>
        <span v-if="comparisonType === 'range'">
            <input type="checkbox" v-model="values.range.less_than_inclusive" id="lessThanEq">
            <label for="lessThanEq">
                <i :class="['fas', 'fa-less-than' + (values.range.less_than_inclusive ? '-equal' : '')]"></i>
            </label>
            <input type="number" v-model="values.range.less_than">
        </span>
        <span v-if="comparisonType === 'equals'">
            <label for="queryValueInt1"><i
                class="fas fa-equals"></i></label>
            <input type="number" v-if="comparisonType === 'equals'"
                v-model="values.equals.value" id="queryValueInt1">
        </span>
    </div>
</template>

<script>
    import BaseTerm from './BaseTerm.vue';

    export default {
        extends: BaseTerm,
        name:    'NumberTerm',
        data:    function () {
            return {
                values: {
                    equals: {
                        value: null
                    },
                    range:  {
                        greater_than:           null,
                        less_than:              null,
                        greater_than_inclusive: null,
                        less_than_inclusive:    null
                    }
                }
            }
        }
    }
</script>