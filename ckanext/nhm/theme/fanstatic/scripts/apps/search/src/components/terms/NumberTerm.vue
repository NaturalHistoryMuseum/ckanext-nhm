<template>
    <div class="flex-container">
        <span v-if="isRange && data.greater_than !== undefined">{{ data.greater_than }}</span>
        <span v-if="isRange && data.greater_than !== undefined">{{ data.greater_than_inclusive ? '≤' : '<' }}</span>
        <FieldsDropdown v-bind:fields="data.fields"></FieldsDropdown>
        <span v-if="isRange && data.less_than !== undefined">{{ data.less_than_inclusive ? '≤' : '<' }}</span>
        <span v-if="isRange && data.less_than !== undefined">{{ data.less_than }}</span>
        <span v-if="!isRange">{{ comparison === 'contains' ? '~' : '=' }}</span>
        <span v-if="!isRange">{{ data.value }}</span>
    </div>
</template>

<script>
    import BaseTerm from './BaseTerm.vue';

    export default {
        extends:  BaseTerm,
        name:     'NumberTerm',
        computed: {
            isRange() {
                return this.comparison === 'range';
            }
        }
    }
</script>