<template>
    <div class="table-grid"
        :style="{gridTemplateColumns: `repeat(${3 + allHeaders.length}, auto) 1fr`}">
        <span class="th small-column">Package</span>
        <span class="th small-column">Resource</span>
        <span class="th small-column">Record</span>
        <span class="th" v-for="headerGroup in headers" :key="headerGroup.id">
            <span v-for="header in headerGroup" :key="header.id" class="term-group">
                {{ header }}
            </span>
        </span>
        <span class="th" v-for="(header, index) in customHeaders" :key="header.id">
            {{ header }}
            <i class="delete-field fas fa-times-circle fa-xs"
                @click="deleteHeader(index)"></i>
        </span>
        <span class="th text-right">
            <a href="#" @click="showFields = !showFields">
                <i class="fas fa-plus-circle"></i>
            </a>
            <transition name="slidedown">
                <div class="floating space-children-v field-picker" v-if="showFields">
                    <input type="text" class="full-width" name="fieldSearch"
                        id="fieldSearch"
                        value="" autocomplete="off" placeholder="field name"
                        v-model="fieldSearch"/>
                    <select class="full-width" size="10">
                        <option v-for="field in fieldList" v-bind:key="field.id"
                            @dblclick="addNewColumn(field)">{{ field }}
                        </option>
                    </select>
                </div>
            </transition>
        </span>

        <template v-for="item in records">
            <span class="td small-column"><a :href="getUrls(item.resource).packageUrl">
                {{ resourceDetails[item.resource].package_name }}
            </a></span>
            <span class="td small-column"><a :href="getUrls(item.resource).resourceUrl">
                {{ resourceDetails[item.resource].name }}
            </a></span>
            <span class="td small-column"><a
                :href="`${getUrls(item.resource).resourceUrl}/record/${item.data._id}`">
                {{ item.data._id }}
            </a></span>
            <span class="td" v-for="headerGroup in allHeaders" :key="headerGroup.id">
                <span v-for="header in headerGroup" :key="header.id" class="term-group">
                    {{ item.data[header] || '--' }}
                </span>
            </span>
            <span></span>
        </template>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';
    import * as d3 from 'd3-collection';

    export default {
        extends:  BaseView,
        name:     'TableView',
        data:     function () {
            return {
                customHeaders: [],
                headers:       []
            }
        },
        computed: {
            allHeaders() {
                return this.headers.concat(this.customHeaders.map(h => [h]))
            }
        },
        methods:  {
            getHeaders() {
                let fields = [];

                d3.values(this.$store.state.filters.items).forEach(f => {
                    if (f.content.fields !== undefined) {
                        fields.push(f.content.fields)
                    }
                });

                this.headers = fields;
            },
            addNewColumn(field) {
                this.customHeaders.push(field);
            },
            deleteHeader(index) {
                this.$delete(this.customHeaders, index);
            },
            updateView() {
                this.getHeaders();
                this.getFieldList();
            }
        }
    }
</script>

<style scoped>

</style>