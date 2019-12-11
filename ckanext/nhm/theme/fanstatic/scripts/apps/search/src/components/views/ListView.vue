<template>
    <div class="flex-container flex-column flex-left full-width" style="margin-top: 15px;">
        <div v-for="(item, index) in records" :key="item.id" class="record-item full-width">
            <div class="record-header">
                <h4 class="record-name">
                    <a :href="`${getDetails(item.resource).resourceUrl}/record/${item.data._id}`">
                        {{ item.data[getDetails(item.resource).titleField] || item.data._id }} </a>
                </h4>
                <span class="record-pkg">
                    <i class="fas fa-archive inline-icon-left"></i>
                    <a :href="getDetails(item.resource).packageUrl">
                        {{ resourceDetails[item.resource].package_name }}
                    </a>
                </span> <span class="indented record-res">
                    ↳
                    <i class="fas fa-list inline-icon-left"></i>
                    <a :href="getDetails(item.resource).resourceUrl">
                        {{ resourceDetails[item.resource].name }}
                    </a>
                </span>
            </div>
            <div class="record-body flex-container flex-stretch-first flex-smallwrap">
                <ul class="list-unstyled">
                    <li v-for="(headerGroup, index) in headers" :key="headerGroup.id">
                    <span>
                        <b v-for="header in headerGroup" :key="header.id" class="term-group">
                            {{ header }}
                        </b>
                    </span> <b>:</b> <span>
                        <span v-for="header in headerGroup" :key="header.id" class="term-group">
                            {{ getValue(item.data, header) || '--' }}
                        </span>
                    </span>
                    </li>
                </ul>
                <img :src="getImages(item, true).thumb"
                     :alt="getImages(item, true).preview"
                     v-if="getImages(item, true) !== null">
            </div>
        </div>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    export default {
        extends: BaseView,
        name:    'ListView',
        data:    function () {
            return {
                showDetails: null
            }
        }
    }
</script>