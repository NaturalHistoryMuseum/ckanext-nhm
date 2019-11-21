<template>
    <div :class="[...filterClasses, 'filter-term']">
        <div class="flex-container">
            <span v-if="termComparison === 'range'">{{ termData.greater_than }}</span>
            <span v-if="termComparison === 'range'">{{ termData.greater_than_inclusive ? '≤' : '<' }}</span>
            <div class="filter-fields fields" :class="fieldsClasses" @click="toggleShowFields">
                <span>{{ fieldsPlaceholder }}</span>
                <transition name="slidedown">
                    <div v-if="showFields" class="floating">
                            <span class="fields"
                                v-for="field in (termData.fields || [])"
                                v-bind:key="field.id">{{ field }}</span>
                    </div>
                </transition>
            </div>
            <span
                v-if="termComparison === 'range'">{{ termData.less_than_inclusive ? '≤' : '<' }}</span>
            <span v-if="termComparison === 'range'">{{ termData.less_than }}</span>
            <span v-if="termComparison !== 'range' && termType !== 'geo'">{{ termComparison === 'contains' ? '~' : '=' }}</span>
            <span
                v-if="termComparison !== 'range' && termType !== 'geo'">{{ termData.value }}</span>
        </div>
        <transition name="slideright">
            <TermEditor v-if="showEditor" :existing-term-id="filterId" :parent-id="filterItem.parent"></TermEditor>
        </transition>
        <div class="filter-buttons">
            <i class="edit-filter fas fa-pencil-alt fa-xs" @click="showEditor = !showEditor"></i>
            <i class="delete-filter fas fa-times fa-xs" @click="deleteSelf"
                v-if="filterItem.parent !== null"></i>
        </div>
    </div>
</template>

<script>
    import FilterBase from './FilterBase.vue';
    import Loading from './Loading.vue';
    import LoadError from './LoadError.vue';
    const TermEditor = import('./TermEditor.vue');

    export default {
        extends:    FilterBase,
        name: 'FilterTerm',
        components: {
            TermEditor: () => ({component: TermEditor, loading: Loading, error: LoadError}),
        },
        data:       function () {
            return {
                showFields: false,
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
            },
            fieldsPlaceholder() {
                if (this.termType === 'geo') {
                    return '[GEO]';
                }
                let numFields = this.termData.fields.length;
                if (numFields === 0) {
                    return '*';
                }
                else if (numFields === 1) {
                    return this.termData.fields[0];
                }
                else {
                    return numFields + ' fields'
                }
            },
            fieldsClasses() {
                let fieldsClasses = this.showFields ? ['expanded'] : [];
                if (this.termData.fields !== undefined && this.termData.fields.length > 1) {
                    fieldsClasses.push('expandable');
                }
                return fieldsClasses;
            }
        },
        methods: {
            toggleShowFields() {
                this.showFields = this.termData.fields.length > 1 ? !this.showFields : false;
            }
        }
    }
</script>