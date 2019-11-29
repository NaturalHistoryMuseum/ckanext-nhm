<template>
    <div></div>
</template>

<script>
    import FieldsDropdown from './FieldsDropdown.vue';

    export default {
        name: 'BaseTerm',
        components: {
            FieldsDropdown
        },
        props: ['data', 'comparison']
    }
</script>