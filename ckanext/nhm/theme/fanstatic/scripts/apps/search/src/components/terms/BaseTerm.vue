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
        props: ['data', 'comparison'],
        computed: {
            showName() {
                return this.data.name !== '' && this.data.name !== undefined;
            }
        }
    }
</script>