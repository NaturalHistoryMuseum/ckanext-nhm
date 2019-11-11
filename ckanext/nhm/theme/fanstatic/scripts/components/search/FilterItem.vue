<template>
    <div
        :class="[[ 'filter-item', 'flex-container', 'flex-stretch-last', 'flex-right', 'flex-wrap', isGroup ? 'filter-group' : 'filter-term' , 'filter-type-' + groupType ]]">
        <a class="group-type" href="#" v-if="isGroup" @click.self="changeGroupType">
            {{ readableGroupType }}<i class="fas fa-sync fa-xs inline-icon-right"></i>
        </a>
        <div v-if="!isGroup" class="flex-container">
            <span v-if="fieldComparison === 'range'">{{ termData.greater_than }}</span>
            <span v-if="fieldComparison === 'range'">{{ termData.greater_than_inclusive ? '≤' : '<' }}</span>
            <div class="filter-fields fields" :class="fieldsClasses" @click="toggleShowFields">
                <span>{{ fieldsPlaceholder }}</span>
                <transition name="slidedown">
                    <div v-if="showFields" class="floating">
                            <span class="fields"
                                v-for="field in termData.fields"
                                v-bind:key="field.id">{{ field }}</span>
                    </div>
                </transition>
            </div>
            <span
                v-if="fieldComparison === 'range'">{{ termData.less_than_inclusive ? '≤' : '<' }}</span>
            <span v-if="fieldComparison === 'range'">{{ termData.less_than }}</span>
            <span
                v-if="fieldComparison !== 'range'">{{ fieldComparison === 'equals' ? '=' : '~' }}</span>
            <span v-if="fieldComparison !== 'range'">{{ termData.value }}</span>
        </div>
        <FilterItem
            v-for="(item, i) in terms"
            v-bind:input-filter-item="item"
            v-bind:nest-level="nestLevel + 1"
            v-bind:resource-ids="resourceIds"
            v-bind:key="item.id"
            v-bind:schema="schema"
            v-bind:ix="i"></FilterItem>
        <FilterItem
            v-for="(item, i) in groups"
            v-bind:input-filter-item="item"
            v-bind:nest-level="nestLevel + 1"
            v-bind:key="item.id"
            v-bind:schema="schema"
            v-bind:ix="i"></FilterItem>
        <FilterAdd v-if="isGroup" v-bind:is-group="isGroup"
            v-bind:siblings="groupEntries"
            v-bind:nest-level="nestLevel"
            v-bind:resource-ids="resourceIds"
            v-bind:key="_uid + '-new'"
            v-bind:schema="schema"></FilterAdd>
        <transition name="slideright">
            <TermEditor v-if="!isGroup && showEditor" v-bind:resource-ids="resourceIds"
                v-bind:schema="schema" v-bind:existing-term="filterItem"></TermEditor>
        </transition>
        <div class="filter-buttons">
            <i class="edit-filter fas fa-pencil-alt fa-xs" @click="showEditor = !isGroup"
                v-if="!isGroup"></i>
            <i class="delete-filter fas fa-times fa-xs" @click="deleteSelf"
                v-if="this.$parent.deleteChild !== undefined"></i>
        </div>
    </div>
</template>

<script>
    import FilterAdd from './FilterAdd.vue';
    import TermEditor from './TermEditor';

    export default {
        name:       'FilterItem',
        components: {
            TermEditor,
            FilterAdd
        },
        props:      {
            schema:          {},
            inputFilterItem: {
                type:      Object,
                default:   function () {
                    return {and: []}
                },
                validator: (value) => {
                    return value.type === undefined ? Object.entries(value).length === 1 : true;
                }
            },
            nestLevel:       {
                type:    Number,
                default: 0
            },
            resourceIds:     {}
        },
        data:       function () {
            let item      = d3.entries(this.inputFilterItem)[0];
            let isGroup   = this.schema.groups.includes(item.key);
            return {
                filterItem:      this.inputFilterItem,
                showFields:      false,
                isGroup:         isGroup,
                groupType:       isGroup ? item.key : '',
                showEditor:      false
            }
        },
        computed:   {
            groupEntries:      function () {
                return d3.entries(this.filterItem)[0].value;
            },
            termData:          function () {
                return this.isGroup ? {} : d3.values(this.filterItem)[0];
            },
            fieldComparison:   function () {
                let item      = d3.entries(this.filterItem)[0];
                return this.isGroup ? '' : item.key.split('_')[1];
            },
            terms:             function () {
                if (!this.isGroup) {
                    return;
                }
                return this.groupEntries.filter((f) => {
                    let filterType = d3.entries(f)[0].key;
                    return !this.schema.groups.includes(filterType);
                })
            },
            groups:            function () {
                if (!this.isGroup) {
                    return;
                }
                return this.groupEntries.filter((f) => {
                    let filterType = d3.entries(f)[0].key;
                    return this.schema.groups.includes(filterType);
                })
            },
            readableGroupType: function () {
                return {
                    'and': 'ALL OF',
                    'or':  'ANY OF',
                    'not': 'NONE OF'
                }[this.groupType];
            },
            fieldsPlaceholder: function () {
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
            fieldsClasses:     function () {
                let fieldsClasses = this.showFields ? ['expanded'] : [];
                if (this.termData.fields.length > 1) {
                    fieldsClasses.push('expandable');
                }
                return fieldsClasses
            }
        },
        methods:    {
            changeGroupType:  function () {
                if (!this.isGroup) {
                    return;
                }
                let entries               = this.groupEntries;
                let ix                    = this.schema.groups.indexOf(this.groupType);
                let newIx                 = ix + 1 >= this.schema.groups.length ? 0 : ix + 1;
                let newGroup              = this.schema.groups[newIx];
                this.$delete(this.filterItem, this.groupType);
                this.$set(this.filterItem, newGroup, entries);
                this.groupType = newGroup;
            },
            toggleShowFields: function () {
                this.showFields = this.termData.fields.length > 1 ? !this.showFields : false;
            },
            deleteSelf:       function () {
                if (this.$parent.deleteChild !== undefined) {
                    this.$parent.deleteChild(this.filterItem)
                }
            },
            deleteChild:      function (item) {
                if (!this.isGroup) {
                    return;
                }
                let ix = this.filterItem[this.groupType].indexOf(item);
                this.$delete(this.filterItem[this.groupType], ix);
            }
        }
    }
</script>