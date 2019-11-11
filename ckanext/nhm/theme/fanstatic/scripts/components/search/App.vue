<template>
    <div class="search-form multisearch-form">
        <div class="multisearch-simple flex-container flex-stretch-first">
            <div class="search-input control-group search-giant">
                <label for="all" class="sr-only">Search</label>
                <input type="text" class="search" name="all" id="all"
                    value="" autocomplete="off" placeholder="Search all fields"
                    v-model="search" @keyup.enter="runSearch"/>
                <button type="submit" @click="runSearch">
                    <i class="fas fa-search"></i>
                    <span class="sr-only">Search</span>
                </button>
            </div>
            <transition name="slidedown">
                <div class="fields resourceid-list floating" v-if="showResources">
                    <input type="checkbox" id="allresources" v-model="allResources">
                    <label for="allresources">All resources</label>
                    <div :class="{ disabled: allResources }">
                        <span v-for="pkg in packageList" v-bind:key="pkg.id">
                        <input type="checkbox" :id="pkg.id" :value="pkg.id"
                            @change="togglePackage($event, pkg)" style="display: none;" checked>
                        <label :for="pkg.id">{{ pkg.name }}</label>
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
                showQuery:     false
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
            getPackageList: function () {
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
            runSearch:      function () {
                const vue = this;
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
                    body:        JSON.stringify({query: this.query}),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.result = data;
                });
            },
            togglePackage:  function (event, pkg) {
                this.allResources = false;
                if (event.target.checked) {
                    this.resourceIds = this.resourceIds.concat(pkg.resourceIds.filter((x) => {
                        return !this.resourceIds.includes(x);
                    }));
                }
                else {
                    this.resourceIds = this.resourceIds.filter((resourceId) => {
                        return !pkg.resourceIds.includes(resourceId);
                    })
                }
            },
            reset:          function () {
                let rootGroup = d3.keys(this.filters)[0];
                this.$delete(this.filters, rootGroup);
                this.$set(this.filters, 'and', []);
            }
        },
        watch:      {
            result: function (result) {
                console.log(result.success);
            }
        }
    }
</script>