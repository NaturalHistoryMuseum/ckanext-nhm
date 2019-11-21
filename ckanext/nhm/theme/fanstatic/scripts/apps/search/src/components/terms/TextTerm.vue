<template>
    <div class="flex-container flex-center">
                    <span class="fields">
                        field
                    </span>
        <label for="queryValueText">
            <i :class="['fas', comparisonType === 'equals' ? 'fa-equals' : 'fa-search' ]"></i>
        </label>
        <input type="text" v-model="values[comparisonType].value" id="queryValueText" size="10">
    </div>
</template>

<script>
    import BaseTerm from './BaseTerm.vue';

    export default {
        extends: BaseTerm,
        name: 'TextTerm',
        data: function () {
            return {
                values: {
                    equals:   {
                        value: null
                    },
                    contains: {
                        value: null
                    }
                }
            }
        }
    }
</script>