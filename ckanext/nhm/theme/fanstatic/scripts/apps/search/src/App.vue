<template>
    <div>
        <Loading v-if="appLoading"></Loading>
        <LoadError v-if="appError"></LoadError>
        <ImageViewer v-if="showImage"></ImageViewer>
        <div class="search-form multisearch-form" v-if="!appLoading && !appError">
            <div class="multisearch-simple flex-container flex-stretch-first flex-smallwrap space-children-v flex-right">
                <div class="search-input control-group search-giant">
                    <label for="all" class="sr-only">Search</label> <input type="text"
                                                                           class="search"
                                                                           name="all"
                                                                           id="all"
                                                                           value=""
                                                                           autocomplete="off"
                                                                           placeholder="Search all fields"
                                                                           v-model="search"
                                                                           @keyup.enter="runSearch(0)"/>
                    <button type="submit" @click="runSearch(0)">
                        <i class="fas fa-search"></i> <span class="sr-only">Search</span>
                    </button>
                </div>
                <div class="flex-container flex-nowrap">
                    <div class="text-right nowrap" style="margin-left: 10px;">
                        <a href="/help/search" target="_blank" class="collapse-to-icon"> Help <i
                            class="fas inline-icon-right fa-question"></i> </a>
                    </div>
                    <div class="text-right nowrap" style="margin-left: 10px;">
                        <a href="#" @click="showAdvanced = !showAdvanced" class="collapse-to-icon">
                            Advanced <i class="fas inline-icon-right"
                                        :class="showAdvanced ? 'fa-minus-circle' : 'fa-plus-circle'"></i>
                        </a>
                    </div>
                    <div class="text-right nowrap" style="margin-left: 10px;">
                        <a href="#" @click="showQuery = !showQuery" class="collapse-to-icon"> Query
                            <i class="inline-icon-right fas"
                               :class="[showQuery ? 'fa-eye-slash' : 'fa-eye']"></i> </a>
                    </div>
                    <div class="text-right nowrap" style="margin-left: 10px;">
                        <a href="#" @click="reset" class="collapse-to-icon"> Reset
                            <i class="inline-icon-right fas fa-trash"></i> </a>
                    </div>
                    <div class="text-right nowrap" style="margin-left: 10px;">
                        <a href="#"
                           @click="showResources = !showResources"
                           id="btnResources"
                           class="collapse-to-icon"> Resources
                            <i class="fas fa-list inline-icon-right"></i> </a>
                    </div>
                    <transition name="slidedown">
                        <ResourceList v-if="showResources"
                                      v-dismiss="{switch: 'showResources', ignore: ['#btnResources']}"></ResourceList>
                    </transition>
                </div>

            </div>
            <transition name="slidedown">
                <div class="multisearch-advanced flex-container" v-if="showAdvanced">
                    <FilterGroup filter-id="group_root"
                                 v-bind:nest-level="0"
                                 key="root"></FilterGroup>
                </div>
            </transition>
            <Copyable :copy-text="JSON.stringify(requestBody)" v-if="showQuery">
                <pre>{{ requestBody }}</pre>
            </Copyable>

            <Results></Results>
        </div>
    </div>
</template>

<script>
    import Loading from './components/Loading.vue';
    import LoadError from './components/LoadError.vue';
    import FilterGroup from './components/FilterGroup.vue';
    import Results from './components/Results.vue';
    import Copyable from './components/misc/Copyable.vue';
    import ImageViewer from './components/misc/ImageViewer.vue';
    import {mapActions, mapMutations, mapState, mapGetters} from 'vuex';

    const ResourceList = import('./components/ResourceList.vue');

    export default {
        name:       'App',
        components: {
            ResourceList: () => ({component: ResourceList, loading: Loading, error: LoadError}),
            Loading,
            LoadError,
            FilterGroup,
            Results,
            Copyable,
            ImageViewer
        },
        data:       function () {
            return {
                showResources: false,
                showAdvanced:  true,
                showQuery:     false
            }
        },
        computed:   {
            ...mapState(['appLoading', 'appError']),
            ...mapGetters('results/query', ['requestBody']),
            ...mapState('results/query/resources', ['packageList', 'resourceIds']),
            ...mapState('results/display', ['showImage']),
            search: {
                get() {
                    return this.$store.state.results.query.search;
                },
                set(value) {
                    this.setSearch(value);
                }
            }
        },
        created:    function () {
            this.getSchema();
            this.getPackageList();
        },
        methods:    {
            ...mapMutations('results/query', ['setSearch']),
            ...mapMutations('results/query/resources', ['selectAllResources']),
            ...mapMutations('results/query/filters', ['resetFilters']),
            ...mapActions(['getSchema']),
            ...mapActions('results', ['runSearch', 'invalidate', 'reset']),
            ...mapActions('results/query', ['setRequestBody']),
            ...mapActions('results/query/resources', ['getPackageList'])
        },
        watch:      {
            packageList: function (newList, oldList) {
                // if no resource ids are pre-selected,
                // select all resource ids once the package list loads
                if (oldList.length === 0 && this.resourceIds.length === 0) {
                    this.selectAllResources();
                }
            },
            requestBody: {
                handler() {
                    this.invalidate();
                },
                deep: true
            }
        }
    }
</script>