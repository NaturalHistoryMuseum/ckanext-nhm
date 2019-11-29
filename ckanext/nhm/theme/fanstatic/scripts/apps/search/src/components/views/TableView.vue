<template>
    <div class="table-grid"
        :style="{gridTemplateColumns: `repeat(${3 + headers.length}, auto) 1fr`}">
        <div class="th small-column">Dataset</div>
        <div class="th small-column">Resource</div>
        <div class="th small-column last-small-column">Record</div>
        <div class="th data-header" v-for="(headerGroup, index) in headers" :key="headerGroup.id">
            <div>
                <span v-for="header in headerGroup" :key="header.id" class="term-group">
                    {{ header }}
                </span>
            </div>
            <div class="flex-container flex-nowrap flex-equal">
                <i class="delete-field fas fa-times-circle fa-xs"
                    @click="removeHeader(index)"></i>
                <i class="move-field fas fa-chevron-circle-left fa-xs"
                    @click="moveHeader({ix: index, by: -1})" v-if="index > 0"></i>
                <i class="move-field fas fa-chevron-circle-right fa-xs"
                    @click="moveHeader({ix: index, by: 1})" v-if="index < (headers.length - 1)"></i>
            </div>
        </div>
        <span class="th text-right">
            <a href="#" @click="showFields = !showFields" :id="'show-fields-' + _uid">
                <i class="fas fa-plus-circle"></i>
            </a>
            <transition name="slidedown">
                <div class="floating space-children-v field-picker" v-if="showFields"
                    v-dismiss="{switch: 'showFields', ignore: ['show-fields-' + _uid]}">
                    <input type="text" class="full-width" name="fieldSearch"
                        id="fieldSearch"
                        value="" autocomplete="off" placeholder="field name"
                        v-model="fieldSearch"/>
                    <select class="full-width" size="10">
                        <option v-for="field in fieldList" v-bind:key="field.id"
                            @dblclick="addCustomHeader(field)">{{ field }}
                        </option>
                    </select>
                </div>
            </transition>
        </span>

        <template v-for="item in records">
            <span class="td small-column"><a :href="getDetails(item.resource).packageUrl">
                {{ resourceDetails[item.resource].package_name }}
            </a></span>
            <span class="td small-column"><a :href="getDetails(item.resource).resourceUrl">
                {{ resourceDetails[item.resource].name }}
            </a></span>
            <span class="td small-column"><a
                :href="`${getDetails(item.resource).resourceUrl}/record/${item.data._id}`">
                {{ item.data._id }}
            </a></span>
            <span class="td" v-for="headerGroup in headers" :key="headerGroup.id">
                <span v-for="header in headerGroup" :key="header.id" class="term-group">
                    {{ getValue(item.data, header) || '--' }}
                </span>
            </span>
            <span></span>
        </template>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    export default {
        extends: BaseView,
        name:    'TableView'
    }
</script>