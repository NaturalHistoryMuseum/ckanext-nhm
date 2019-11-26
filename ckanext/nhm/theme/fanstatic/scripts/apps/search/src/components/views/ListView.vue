<template>
    <div class="flex-container flex-column flex-left full-width">
        <div v-for="item in records" :key="item.id" class="record-item full-width">
            <h4>Record <a :href="`${getUrls(item.resource).resourceUrl}/record/${item.data._id}`">
                {{ item.data._id }}</a></h4>
            <span>
                <i class="fas fa-list"></i>
                <a :href="getUrls(item.resource).packageUrl">
                    {{ resourceDetails[item.resource].package_name }}
                </a>
                <i class="fas fa-box inline-icon-right"></i>
                <a :href="getUrls(item.resource).resourceUrl">
                    {{ resourceDetails[item.resource].name }}
                </a>
            </span>
        </div>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    export default {
        extends: BaseView,
        name:    'ListView',
    }
</script>

<style scoped>
    .record-item {
        border-bottom: 2px solid black;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }
</style>