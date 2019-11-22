<template>
    <div>
        <Loading v-if="loading"></Loading>
        <LoadError v-if="loadError"></LoadError>
        <div class="search-form multisearch-form" v-if="!loading && !loadError">
            <div class="multisearch-simple flex-container flex-stretch-first">
                <div class="search-input control-group search-giant">
                    <label for="all" class="sr-only">Search</label>
                    <input type="text" class="search" name="all" id="all"
                        value="" autocomplete="off" placeholder="Search all fields"
                        v-model="search" @keyup.enter="runSearch(0)"/>
                    <button type="submit" @click="runSearch(0)">
                        <i class="fas fa-search"></i>
                        <span class="sr-only">Search</span>
                    </button>
                </div>
                <transition name="slidedown">
                    <ResourceList v-if="showResources"></ResourceList>
                </transition>
                <div class="text-right" style="margin-left: 10px;">
                    <a href="#" @click="showResources = !showResources">
                        Resources <i class="fas fa-list inline-icon-right"></i>
                    </a>
                </div>
                <div class="text-right" style="margin-left: 10px;">
                    <a href="#" @click="showAdvanced = !showAdvanced">
                        Advanced <i class="fas inline-icon-right"
                        :class="showAdvanced ? 'fa-minus-circle' : 'fa-plus-circle'"></i>
                    </a>
                </div>
                <div class="text-right" style="margin-left: 10px;">
                    <a href="#" @click="showQuery = !showQuery">
                        Query <i class="inline-icon-right fas"
                        :class="[showQuery ? 'fa-eye-slash' : 'fa-eye']"></i>
                    </a>
                </div>
                <div class="text-right" style="margin-left: 10px;">
                    <a href="#" @click="resetFilters">
                        Reset <i class="inline-icon-right fas fa-trash"></i>
                    </a>
                </div>
            </div>
            <transition name="slidedown">
                <div class="multisearch-advanced flex-container" v-if="showAdvanced">
                    <FilterGroup filter-id="group_1" v-bind:nest-level="0" key="root">
                    </FilterGroup>
                </div>
            </transition>
            <pre class="fields" v-if="showQuery">{{ query }}</pre>
            <Results></Results>
        </div>
    </div>
</template>

<script>
    import Loading from './components/Loading.vue';
    import LoadError from './components/LoadError.vue';
    import FilterGroup from './components/FilterGroup.vue';
    import Results from './components/Results.vue';
    import {mapGetters, mapMutations, mapState, mapActions} from 'vuex';

    const ResourceList = import('./components/ResourceList.vue');

    export default {
        name:       'App',
        components: {
            ResourceList: () => ({component: ResourceList, loading: Loading, error: LoadError}),
            Loading,
            LoadError,
            FilterGroup,
            Results
        },
        data:       function () {
            return {
                showResources: false,
                showAdvanced:  true,
                showQuery:     false
            }
        },
        computed:   {
            ...mapState('constants', ['loading', 'loadError', 'packageList']),
            ...mapGetters(['query']),
            search: {
                get() {
                    return this.$store.state.search;
                },
                set(value) {
                    this.$store.commit('setSearch', value)
                }
            }
        },
        created:    function () {
            this.$store.dispatch('constants/getSchema');
            this.$store.dispatch('constants/getPackageList');
        },
        methods:    {
            ...mapActions('results', ['runSearch']),
            ...mapMutations('filters', ['resetFilters']),
            ...mapMutations('results', ['invalidateSlug'])
        },
        watch: {
            packageList: function (newList, oldList) {
                if (oldList.length === 0) {
                    this.$store.commit('selectAllResources');
                }
            },
            query: function () {
                this.invalidateSlug();
            }
        }
    }
</script>