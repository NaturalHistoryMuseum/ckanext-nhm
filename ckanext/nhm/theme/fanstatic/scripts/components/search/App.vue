<template>
    <div class="search-form multisearch-form">
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
                <div class="fields resourceid-list floating flex-container flex-column flex-left"
                    v-if="showResources">
                    <div>
                        <input type="checkbox" id="allresources" v-model="allResources">
                        <label for="allresources">All resources</label>
                    </div>
                    <div>
                        <input type="checkbox" id="toggleAll" v-model="allResourcesToggle" @change="toggleAllResources">
                        <label for="toggleAll">Select all</label>
                    </div>
                    <div :class="{ disabled: allResources }">
                        <span v-for="pkg in packageList" v-bind:key="pkg.id">
                        <a href="#" :id="pkg.id" :value="pkg.id"
                            @click="togglePackage(pkg)">{{ pkg.name }}</a>
                        <div class="fields">
                            <span v-for="resource in pkg.resources" v-bind:key="resource.id">
                                <input type="checkbox" :id="resource.id" :value="resource.id"
                                    v-model="resourceIds">
                                <label :for="resource.id">{{ resource.name }}</label>
                            </span>
                        </div>
                        </span>
                    </div>
                </div>
            </transition>
            <div class="text-right" style="margin-left: 10px;">
                <a href="#" @click="showResources = !showResources">Resources <i
                    class="fas fa-list inline-icon-right"></i></a>
            </div>
            <div class="text-right" style="margin-left: 10px;">
                <a href="#" @click="showAdvanced = !showAdvanced">Advanced <i
                    class="fas inline-icon-right"
                    :class="showAdvanced ? 'fa-minus-circle' : 'fa-plus-circle'"></i></a>
            </div>
            <div class="text-right" style="margin-left: 10px;">
                <a href="#" @click="showQuery = !showQuery">Query <i class="inline-icon-right fas"
                    :class="[showQuery ? 'fa-eye-slash' : 'fa-eye']"></i></a>
            </div>
            <div class="text-right" style="margin-left: 10px;">
                <a href="#" @click="reset">Reset <i class="inline-icon-right fas fa-trash"></i></a>
            </div>
        </div>
        <transition name="slidedown">
            <div class="multisearch-advanced flex-container" v-if="showAdvanced">
                <FilterItem v-bind:input-filter-item="filters" v-bind:nest-level="0" key="root"
                    v-bind:schema="schema" v-bind:resource-ids="allResources ? null : resourceIds">
                </FilterItem>
            </div>
        </transition>
        <pre class="fields" v-if="showQuery">{{ query }}</pre>
        <Results></Results>
        <div class="pagination-wrapper">
            <ul class="pagination">
                <li v-if="currentPage > 0">
                    <a href="#" @click="runSearch(currentPage - 1)">{{ currentPage }}</a>
                </li>
                <li class="active">
                    <a href="#">{{ currentPage + 1 }}</a>
                </li>
                <li v-if="after.length > 0">
                    <a href="#" @click="runSearch(currentPage + 1)">{{ currentPage + 2}}</a>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
    import FilterItem from './FilterItem';
    import Results from './Results';
    import $RefParser from 'json-schema-ref-parser';

    export default {
        name:       'App',
        refParser:  $RefParser,
        components: {
            FilterItem,
            Results
        },
        props:      ['schema'],
        data:       function () {
            return {
                search:        '',
                filters:       {
                    'and': [
                        {
                            'string_equals': {
                                'fields': [
                                    'genus',
                                    'Genus'
                                ],
                                'value':  'helix'
                            }
                        }
                    ]
                },
                result:        {},
                resourceIds:   [],
                packageList:   [],
                showResources: false,
                showAdvanced:  true,
                allResources:  true,
                allResourcesToggle: true,
                showQuery:     false,
                after:         [],
                currentPage:   0
            }
        },
        mounted:    function () {
            // it'd be nice to use v-cloak for this but because we generally load the vue
            // lib after the page is rendered it's too late for the elements with the attr
            // to actually be hidden from view. This does essentially the same thing, by
            // manually removing the hide-until-loaded class on all elements that have it
            $('.hide-until-loaded').removeClass('hide-until-loaded');
            document.getElementById('all').focus();

            this.getPackageList();
        },
        computed:   {
            query: function () {
                let q = {
                    query_version: 'v1.0.0'
                };
                if (this.search !== null && this.search !== '') {
                    q.search = this.search;
                }
                if (d3.values(this.filters).some((f) => f.length > 0)) {
                    q.filters = this.filters;
                }
                return q;
            }
        },
        methods:    {
            getPackageList:     function () {
                const vue = this;
                fetch('/api/3/action/current_package_list_with_resources', {
                    method: 'GET'
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.packageList = data.result.map(pkg => {
                        let resources = pkg.resources.filter(r => {
                            return r.datastore_active;
                        }).map(r => {
                            return {
                                name: r.name,
                                id:   r.id
                            }
                        });
                        return {
                            name:        pkg.name,
                            id:          pkg.id,
                            resources:   resources,
                            resourceIds: resources.map(r => r.id)
                        }
                    }).filter(pkg => pkg.resources.length > 0);
                    vue.packageList.forEach((pkg) => {
                        vue.resourceIds = vue.resourceIds.concat(pkg.resourceIds)
                    });
                });
            },
            runSearch:          function (page) {
                const vue = this;
                let body  = {
                    query:        this.query,
                    resource_ids: this.resourceIds
                };
                if (page > 0) {
                    body.after = this.after[page - 1];
                }
                else {
                    this.after = [];
                }

                fetch('/api/3/action/datastore_multisearch', {
                    method:      'POST',
                    mode:        'cors',
                    cache:       'no-cache',
                    credentials: 'same-origin',
                    headers:     {
                        'Content-Type': 'application/json'
                    },
                    redirect:    'follow',
                    referrer:    'no-referrer',
                    body:        JSON.stringify(body),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.result = data;
                    if (data.success && data.result.after !== null) {
                        if (vue.after.indexOf(data.result.after) < 0) {
                            vue.after.push(data.result.after);
                            vue.currentPage = page;
                        }
                    }
                    else {
                        console.error(data);
                        console.error(JSON.stringify(body));
                    }
                });
            },
            togglePackage:      function (pkg) {
                this.allResources = false;
                let isInResources = pkg.resourceIds.some((r) => {
                    return this.resourceIds.includes(r);
                });
                if (isInResources) {
                    this.resourceIds = this.resourceIds.filter((resourceId) => {
                        return !pkg.resourceIds.includes(resourceId);
                    });
                }
                else {
                    this.resourceIds = this.resourceIds.concat(pkg.resourceIds.filter((x) => {
                        return !this.resourceIds.includes(x);
                    }));
                }
            },
            reset:              function () {
                let rootGroup = d3.keys(this.filters)[0];
                this.$delete(this.filters, rootGroup);
                this.$set(this.filters, 'and', []);
            },
            toggleAllResources: function (event) {
                this.allResources = false;
                this.resourceIds  = [];
                if (event.target.checked) {
                    this.packageList.forEach((pkg) => {
                        this.resourceIds = this.resourceIds.concat(pkg.resourceIds)
                    });
                }
                else {
                    this.resourceIds = [];
                }
            }
        },
        watch: {
            resourceIds: function (resourceIds, oldResourceIds) {
                this.allResources = false;
                if (resourceIds.length < oldResourceIds.length) {
                    this.allResourcesToggle = false;
                }
            }
        }
    }
</script>