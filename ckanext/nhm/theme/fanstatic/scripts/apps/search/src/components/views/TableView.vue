<template>
    <div class="table-grid"
        :style="{gridTemplateColumns: `repeat(${3 + headers.length}, auto) 1fr`}">
        <span class="th small-column">Package</span>
        <span class="th small-column">Resource</span>
        <span class="th small-column last-small-column">Record</span>
        <span class="th" v-for="(headerGroup, index) in headers" :key="headerGroup.id">
            <span>
                <span v-for="header in headerGroup" :key="header.id" class="term-group">
                    {{ header }}
                </span>
            </span>
            <i class="delete-field fas fa-times-circle fa-xs"
                @click="removeHeader(index)"></i>
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