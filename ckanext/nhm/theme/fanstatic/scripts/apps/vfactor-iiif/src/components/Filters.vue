<template>
    <div class="module module-narrow module-shallow">
        <h2 class="module-heading">
            <i class="fas fa-filter fa-lg inline-icon-left"></i>Filters
        </h2>
        <div class="module-content">
            <div>
                If you know what drawer you're looking for, please select its barcode from the
                dropdown below. If not, use the checkboxes to filter your search by collection.
            </div>
            <div class="viiif-intro-text-lower">
                Please be aware that you cannot use both of these options at the same time.
            </div>
            <hr/>
            <div :class="{'viiif-filter': true, 'active': activeFilter === 'barcode'}">
                <label class="viiif-filter-barcode-label" for="viiif-filter-barcode-select">
                    Select a barcode:
                </label>
                <div class="viiif-filter-barcode-body">
                    <select id="viiif-filter-barcode-select" v-model="barcode">
                        <option disabled value="">Please select one</option>
                        <option v-for="option in barcodes" :value="option" :key="option">
                            {{ option }}
                        </option>
                    </select>
                    <button class="btn btn-primary" :disabled="barcode == null"
                            @click="changeBarcode">View drawer
                    </button>
                </div>
            </div>
            <hr/>
            <div :class="{'viiif-filter': true, 'active': activeFilter === 'collections'}">
                <div class="viiif-filter-collection-label-header">
                    Or choose one or more collections to view:
                </div>
                <div v-for="option in collectionNames">
                    <label class="viiif-filter-collection-label">
                        <input type="checkbox" :value="option" v-model="collections">
                        {{ option }}
                    </label>
                </div>
                <div class="viiif-filter-collection-actions">
                    <div class="viiif-filter-collection-selectors">
                        <span class="viiif-filter-collection-selector"
                              @click="selectAll">Select all</span>
                        <span class="viiif-filter-collection-selector"
                              @click="deselectAll">Clear</span>
                    </div>
                    <button class="btn btn-primary" :disabled="collections.length === 0"
                            @click="changeCollections">
                        {{'View collection' | pluralize(collections)}}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from "axios";

    export default {
        name: "Filters",
        props: {
            resourceId: {
                type: String,
                required: true
            },
            query: {
                type: Object,
                default: {}
            }
        },
        data() {
            return {
                barcodes: [],
                collectionNames: [],
                barcode: null,
                collections: [],
                activeFilter: null
            }
        },
        created() {
            axios.post('/api/3/action/datastore_multisearch', {
                resource_ids: [this.resourceId],
                query: this.query,
                // we know that the number of records in this resource is 400 so we can just get
                // them all straight up
                size: 400
            }).then(response => {
                for (const record of response.data.result.records) {
                    this.barcodes.push(record.data.Barcode);
                    const name = record.data['Collection Name'];
                    if (!this.collectionNames.includes(name)) {
                        this.collectionNames.push(name);
                    }
                }
                this.barcodes.sort();
                this.collectionNames.sort();

                // start off with everything selected
                this.selectAll();
                this.changeCollections();
            }).catch(error => {
                console.log(error);
            });
        },
        methods: {
            selectAll() {
                for (const collection of this.collectionNames) {
                    if (!this.collections.includes(collection)) {
                        this.collections.push(collection);
                    }
                }
            },
            deselectAll() {
                this.collections = [];
            },
            changeCollections() {
                this.activeFilter = 'collections';
                this.$emit('collections-change', this.collections);
            },
            changeBarcode() {
                this.activeFilter = 'barcode';
                this.$emit('barcode-change', this.barcode);
            }
        },
        filters: {
            trim(value) {
                return value.trim();
            },
            pluralize: function (value, collections) {
                if (collections.length > 1) {
                    return `${value}s`;
                }
                return value;
            }
        }
    }
</script>
