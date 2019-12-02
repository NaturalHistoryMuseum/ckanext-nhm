<template>
    <div :class="[...filterClasses, 'filter-group', 'filter-type-' + filterKey]">
        <a class="group-type" href="#" @click.self="changeGroupType">
            {{ readableGroupType }}
        </a>
        <FilterTerm
            v-for="id in subTerms"
            v-bind:filter-id="id"
            v-bind:key="id.id"></FilterTerm>
        <FilterGroup
            v-for="id in subGroups"
            v-bind:filter-id="id"
            v-bind:key="id.id"></FilterGroup>
        <FilterAdd v-bind:parent-id="filterId" v-bind:key="_uid + '-new'"></FilterAdd>
        <div class="filter-buttons">
            <i class="delete-filter fas fa-times fa-xs" @click="deleteSelf"
                v-if="filterItem.parent !== null"></i>
        </div>
    </div>
</template>

<script>
    import FilterBase from './FilterBase.vue';
    import FilterTerm from './FilterTerm.vue';
    import FilterAdd from './FilterAdd.vue';
    import {mapState, mapGetters, mapMutations} from 'vuex';

    export default {
        extends:    FilterBase,
        name: 'FilterGroup',
        components: {
            FilterAdd,
            FilterTerm
        },
        computed:   {
            ...mapGetters('constants', ['getGroup']),
            ...mapGetters('filters', ['getChildren']),
            subTerms() {
                return this.getChildren(this.filterId, true).filter((f) => {
                    return !f.key.startsWith('group_');
                }).map(f => f.key);
            },
            subGroups() {
                return this.getChildren(this.filterId, true).filter((f) => {
                    return f.key.startsWith('group_');
                }).map(f => f.key);
            },
            readableGroupType() {
                return this.getGroup(this.filterKey);
            },
        },
        methods:    {
            ...mapMutations('filters', ['changeKey']),
            changeGroupType() {
                let ix       = this.schema.groups.indexOf(this.filterKey);
                let newIx    = ix + 1 >= this.schema.groups.length ? 0 : ix + 1;
                let newGroup = this.schema.groups[newIx];
                this.changeKey({
                    id:     this.filterId,
                    key: newGroup
                });
            }
        }
    }
</script>