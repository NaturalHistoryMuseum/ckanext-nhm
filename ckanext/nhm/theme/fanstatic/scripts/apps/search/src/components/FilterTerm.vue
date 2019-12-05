<template>
    <div :class="[...filterClasses, 'filter-term']">
        <component :is="termType"
                   v-bind:data="termData"
                   v-bind:comparison="termComparison"></component>
        <transition name="slideright">
            <TermEditor v-if="showEditor"
                        :existing-term-id="filterId"
                        :parent-id="filterItem.parent"
                        v-dismiss="{switch: 'showEditor', ignore: ['#show-editor-' + _uid]}"></TermEditor>
        </transition>
        <div class="filter-buttons">
            <i class="edit-filter fas fa-pencil-alt fa-xs"
               @click="showEditor = !showEditor"
               :id="'show-editor-' + _uid"></i> <i class="delete-filter fas fa-times fa-xs"
                                                   @click="deleteSelf"
                                                   v-if="filterItem.parent !== null"></i>
        </div>
    </div>
</template>

<script>
    import FilterBase from './FilterBase.vue';
    import Loading from './Loading.vue';
    import LoadError from './LoadError.vue';

    const TermEditor = import('./TermEditor.vue');
    const TextTerm   = import('./terms/TextTerm.vue');
    const NumberTerm = import('./terms/NumberTerm.vue');
    const GeoTerm    = import('./terms/GeoTerm.vue');
    const OtherTerm  = import('./terms/OtherTerm.vue');

    export default {
        extends:    FilterBase,
        name:       'FilterTerm',
        components: {
            TermEditor: () => ({component: TermEditor, loading: Loading, error: LoadError}),
            string:     () => ({component: TextTerm, loading: Loading, error: LoadError}),
            number:     () => ({component: NumberTerm, loading: Loading, error: LoadError}),
            geo:        () => ({component: GeoTerm, loading: Loading, error: LoadError}),
            other:      () => ({component: OtherTerm, loading: Loading, error: LoadError})
        },
        data:       function () {
            return {
                showEditor: false
            }
        },
        computed:   {
            termData() {
                return this.filterItem.content;
            },
            termType() {
                if (!this.filterKey.includes('_')) {
                    return 'other';
                }
                else {
                    return this.filterKey.split('_')[0]
                }
            },
            termComparison() {
                return this.filterKey.slice(this.filterKey.indexOf('_') + 1);
            }
        },

    }
</script>