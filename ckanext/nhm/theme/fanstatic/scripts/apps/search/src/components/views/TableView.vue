<template>
    <div class="table-grid"
        :style="{gridTemplateColumns: 'repeat(4, max-content)' + (headers.length > 0 ? `repeat(${headers.length}, auto)` : '')}">
        <div class="th small-column"></div>
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

        <template v-for="(item, ix) in records">
            <div class="td small-column">{{ (page * 100) + ix + 1 }}</div>
            <div class="td small-column"><a :href="getDetails(item.resource).packageUrl">
                {{ resourceDetails[item.resource].package_name }}
            </a></div>
            <div class="td small-column"><a :href="getDetails(item.resource).resourceUrl">
                {{ resourceDetails[item.resource].name }}
            </a></div>
            <div class="td small-column"><a
                :href="`${getDetails(item.resource).resourceUrl}/record/${item.data._id}`">
                {{ item.data._id }}
            </a></div>
            <div class="td" v-for="headerGroup in headers" :key="headerGroup.id">
                <span v-for="header in headerGroup" :key="header.id" class="term-group">
                    {{ getValue(item.data, header) || '--' }}
                </span>
            </div>
        </template>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    export default {
        extends:    BaseView,
        name:       'TableView'
    }
</script>