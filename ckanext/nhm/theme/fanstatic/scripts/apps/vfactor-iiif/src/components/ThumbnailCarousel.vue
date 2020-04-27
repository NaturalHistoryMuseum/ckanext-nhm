<template>
    <div>
        <div class="viiif-thumbnail-header">
            Showing {{ records.length }} of {{ total }} total thumbnails
        </div>
        <div class="viiif-thumbnail-track" @mousedown="onMouseDown" @mouseleave="onMouseLeave"
             @mouseup="onMouseUp" @mousemove="onMouseMove" @scroll="onScroll"
             @contextmenu="onRightClick" ref="track">
            <div :class="{'viiif-thumbnail-container': true, 'active': currentIndex === index}"
                 v-for="(record, index) in records"
                 :key="record._id" :data-thumbnail-index="index" ref="container">
                <img class="viiif-thumbnail-image" :src="getRecordThumbnail(record)"
                     :width="`${thumbnailSize}px`" draggable="false"/>
                <div class="viiif-thumbnail-label">
                    <div class="viiif-thumbnail-label-barcode">
                        {{ record.Barcode }}
                    </div>
                    <div class="viiif-thumbnail-label-collection">
                        {{ record['Collection Name'] }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "ThumbnailCarousel",
        props: {
            records: {
                type: Array,
                required: true
            },
            manifests: {
                type: Object
            },
            moreRecordsAvailable: {
                type: Boolean,
                required: true
            },
            total: {
                type: Number,
                required: true
            },
            thumbnailSize: {
                type: Number,
                default: 200
            },
            mouseClickMoveThreshold: {
                type: Number,
                default: 5
            }
        },
        data() {
            return {
                currentIndex: 0,
                sliding: false,
                isDown: false,
                startX: 0,
                scrollLeft: 0,
                waitingForMore: false
            }
        },
        watch: {
            records(newRecords, oldRecords) {
                this.waitingForMore = false;

                if (oldRecords.length > 0 && newRecords.length > 0 &&
                    oldRecords[0]._id !== newRecords[0]._id) {
                    this.$refs.track.scrollLeft = 0;
                    this.goto(0);
                }
            }
        },
        methods: {
            getRecordThumbnail(record) {
                const iiifManifest = this.manifests[record._id];
                if (!!iiifManifest) {
                    const infoUrl = iiifManifest.items[0].items[0].items[0].body.id;
                    // 10 is the length of "info.json"
                    const baseUrl = infoUrl.slice(0, infoUrl.length - 10);
                    return `${baseUrl}/full/${this.thumbnailSize},/0/default.jpg`
                }
                return '';
            },
            onMouseDown(event) {
                this.isDown = true;
                this.sliding = true;
                this.startX = event.pageX;
                this.scrollLeft = this.$refs.track.scrollLeft;
            },
            onRightClick() {
                // just use the mouse leave logic
                this.onMouseLeave();
            },
            onMouseLeave() {
                this.isDown = false;
                this.sliding = false;
            },
            onMouseUp(event) {
                this.isDown = false;
                this.sliding = false;
                if (this.startX >= event.pageX - this.mouseClickMoveThreshold &&
                    this.startX <= event.pageX + this.mouseClickMoveThreshold) {
                    let index = null;
                    if (event.target.classList.contains('viiif-thumbnail-image') ||
                        event.target.classList.contains('viiif-thumbnail-label')) {
                        index = parseInt(event.target.parentElement.dataset.thumbnailIndex);
                    } else if (event.target.classList.contains('viiif-thumbnail-container')) {
                        index = parseInt(event.target.dataset.thumbnailIndex);
                    }
                    if (index != null) {
                        this.goto(index);
                    }
                }
            },
            onMouseMove(event) {
                if (!this.isDown) return;
                event.preventDefault();
                const x = event.pageX;
                const walk = x - this.startX;
                this.$refs.track.scrollLeft = this.scrollLeft - walk;
            },
            onScroll(event) {
                if (!this.waitingForMore && this.moreRecordsAvailable) {
                    const scroll = event.target.scrollLeft + event.target.offsetWidth;
                    if (scroll / event.target.scrollWidth >= 0.9) {
                        console.log('requesting more');
                        this.waitingForMore = true;
                        this.$emit('get-more-records');
                    }
                }
            },
            goto(index) {
                this.currentIndex = index;
                this.$emit('slide-change', this.currentIndex);
            }
        }
    }
</script>
