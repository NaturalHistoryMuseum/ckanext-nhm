<template>
    <div class="flex-container">
        <FieldsDropdown v-bind:fields="data.fields"></FieldsDropdown>
        <span>{{ comparison }}</span>
    </div>
</template>

<script>
    import BaseTerm from './BaseTerm.vue';

    export default {
        extends:  BaseTerm,
        name:     'OtherTerm'
    }
</script>