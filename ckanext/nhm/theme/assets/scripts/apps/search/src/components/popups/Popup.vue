<template>
    <div class="info-popup-button">
        <transition name="slidedown">
            <div class="floating info-popup" :class="classes"
                 v-if="showPopup"
                 v-dismiss="dismiss">
                <slot v-on:close-popup="endPopup" v-on:open-popup="startPopup"></slot>
            </div>
        </transition>
        <a href="#" @click="togglePopup" class="btn btn-disabled" :id="popupId">
            <i class="fas" :class="icon"></i>{{ label }}
        </a>
    </div>
</template>

<script>
export default {
    name: 'Popup',
    props: {
        popupId: {
            type: String
        },
        icon: {
            type: String
        },
        label: {
            type: String
        },
        ignoreAdditional: {
            type: Array,
            default: () => []
        },
        classes: {
            type: String
        },
        parentToggle: {
            // toggle signal from parent
            type: Boolean
        }
    },
    data: function () {
        return {
            showPopup: false
        };
    },
    computed: {
        dismiss() {
            let ignoreIds = [...this.ignoreAdditional];
            ignoreIds.push(this.popupId);
            ignoreIds = ignoreIds.map(i => `#${ i }`);
            return { switch: 'showPopup', ignore: ignoreIds };
        }
    },
    methods: {
        startPopup() {
            this.showPopup = true;
        },
        endPopup() {
            this.showPopup = false;
        },
        togglePopup() {
            this.showPopup = !this.showPopup;
        }
    },
    watch: {
        parentToggle() {
            this.showPopup = this.parentToggle;
        },
        showPopup() {
            this.$emit('toggle', this.showPopup)
        }
    }
};
</script>

<style scoped>

</style>
