<template>
    <div class="filter-add">
        <i class="fas fa-plus-square fa-lg" @click="showChoice = !showChoice"
            :id="'show-choice-' + _uid"></i>
        <transition name="slidedown">
            <div class="filter-add-choice floating" v-if="showChoice"
                v-dismiss="{switch: 'showChoice', ignore: ['#show-choice-' + _uid]}">
                <span v-if="canAddGroups" @click="newGroup" :id="'show-editor-groups-' + _uid">new group</span>
                <div v-if="canAddTerms"><span @click="showEditor = true"
                    :id="'show-editor-terms-' + _uid">new term</span>
                <span @click="showPresets = true"
                    :id="'show-editor-presets-' + _uid">presets</span></div>
            </div>
        </transition>
        <transition name="slideright">
            <TermEditor v-if="showEditor" :parent-id="parentId"
                v-dismiss="{switch: 'showEditor', ignore: ['#show-editor-groups-' + _uid, '#show-editor-terms-' + _uid, '.delete-field']}"></TermEditor>
        </transition>
        <transition name="slideright">
            <div v-if="showPresets" class="floating preset-picker"
                v-dismiss="{switch: 'showPresets', ignore: ['#show-editor-presets-' + _uid]}">
                <select size="5">
                    <option v-for="(presetName, presetKey) in presetKeys" v-bind:key="presetKey"
                        @dblclick="newPreset(presetKey)">
                        {{ presetName }}
                    </option>
                </select>
            </div>
        </transition>
    </div>
</template>

<script>
    import Loading from './Loading.vue';
    import LoadError from './LoadError.vue';
    import {mapGetters, mapMutations} from 'vuex';

    const TermEditor = import('./TermEditor.vue');

    export default {
        name:       'FilterAdd',
        props:      ['parentId'],
        components: {
            TermEditor: () => ({component: TermEditor, loading: Loading, error: LoadError}),
        },
        data:       function () {
            return {
                showChoice:  false,
                showEditor:  false,
                showPresets: false
            }
        },
        computed:   {
            ...mapGetters('filters', ['getNestLevel', 'presetKeys']),
            nestLevel() {
                return this.getNestLevel(this.parentId);
            },
            canAddGroups: function () {
                return this.nestLevel === 0;
            },
            canAddTerms:  function () {
                return true;
            }
        },
        methods:    {
            ...mapMutations('filters', ['addGroup', 'addPreset']),
            newGroup: function () {
                this.showChoice = false;
                this.addGroup(this.$parent.filterId);
            },
            newPreset(presetKey) {
                this.addPreset({key: presetKey, parent: this.parentId});
                this.showPresets = false;
            },
        },
        watch: {
            showChoice(v) {
                if (v) {
                    this.showEditor = false;
                    this.showPresets = false;
                }
            },
            showEditor(v) {
                if (v) {
                    this.showChoice = false;
                    this.showPresets = false;
                }
            },
            showPresets(v) {
                if (v) {
                    this.showChoice = false;
                    this.showEditor = false;
                }
            }
        }
    }
</script>