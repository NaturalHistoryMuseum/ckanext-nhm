<template>
    <div>
        <div class="secondary col-sm-3">
            <Filters :query="baseQuery" v-on:barcode-change="onBarcodeChange"
                     v-on:collections-change="onCollectionsChange" :resourceId="resourceId" />
        </div>
        <div class="col-sm-9 col-xs-12">
            <OpenSeadragonView width="100%" height="550px" :currentRecord="currentRecord"
                               :resourceId="resourceId"/>
            <ThumbnailCarousel :records="records" :moreRecordsAvailable="moreRecordsAvailable"
                               :total="total" :thumbnailSize="150" @slide-change="onSlideChange"
                               @get-more-records="onMoreRecordsRequest"/>
        </div>
    </div>
</template>

<script>
    import axios from 'axios';
    import {parse as parseJSON} from 'json-bigint';
    import OpenSeadragonView from './components/OpenSeadragonView.vue';
    import ThumbnailCarousel from './components/ThumbnailCarousel.vue';
    import Filters from './components/Filters.vue';

    export default {
        name: 'App',
        props: {
            resourceId: {
                type: String,
                required: true
            }
        },
        data() {
            return {
                filterQuery: null,
                records: [],
                total: 0,
                currentRecord: null,
                after: null,
                baseQuery: {
                    'filters': {
                        'and': [
                            {
                                'exists': {
                                    'fields': [
                                        'Image'
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        computed: {
            moreRecordsAvailable() {
                return this.after != null;
            }
        },
        created() {
            this.getRecords();
        },
        methods: {
            getRecords(isMoreRequest = false) {
                if (this.filterQuery === null) {
                    this.onRecordsChange([], isMoreRequest);
                    this.after = null;
                    this.total = 0;
                } else {
                    const query = JSON.parse(JSON.stringify(this.baseQuery));
                    query.filters.and.push(this.filterQuery);
                    const body = {
                        resource_ids: [this.resourceId],
                        query: query,
                        size: 15
                    };
                    if (isMoreRequest) {
                        body.after = this.after;
                    }
                    axios.post('/api/3/action/datastore_multisearch', body,
                        // this stops axios parsing the json response automatically so that we can do it
                        {transformResponse: [data => data]}
                    ).then(response => {
                        // use JSONbig to make sure we parse the enormous ints in the after correctly
                        const jsonData = parseJSON(response.data);

                        // grab the after and total
                        this.after = jsonData.result.after;
                        this.total = jsonData.result.total;

                        // then update the records
                        this.onRecordsChange(jsonData.result.records, isMoreRequest);
                    }).catch(error => {
                        console.log(error);
                    });
                }
            },
            onRecordsChange(newRecords, isMoreRequest = false) {
                const records = newRecords.map((record) => record.data);
                if (isMoreRequest) {
                    this.records.push(...records);
                } else {
                    this.records = [...records];
                    this.onSlideChange(0);
                }
            },
            onBarcodeChange(barcode) {
                this.filterQuery = {
                    string_equals: {
                        fields: ['Barcode'],
                        value: barcode
                    }
                };
                this.getRecords();
            },
            onCollectionsChange(collections) {
                switch (collections.length) {
                    case 0:
                        this.filterQuery = null;
                        break;
                    case 1:
                        this.filterQuery = {
                            string_equals: {
                                fields: ['Collection Name'],
                                value: collections[0]
                            }
                        };
                        break;
                    default:
                        this.filterQuery = {
                            or: collections.map(collection => ({
                                string_equals: {
                                    fields: ['Collection Name'],
                                    value: collection
                                }
                            }))
                        };
                        break;
                }
                this.getRecords();
            },
            onSlideChange(index) {
                if (this.records.length > 0) {
                    this.currentRecord = this.records[index];
                } else {
                    this.currentRecord = null;
                }
            },
            onMoreRecordsRequest() {
                this.getRecords(true);
            }
        },
        components: {
            Filters,
            OpenSeadragonView,
            ThumbnailCarousel
        }
    }
</script>
