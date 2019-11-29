<template>
    <div class="filter-add">
        <i class="fas fa-plus-square fa-lg" @click="showChoice = !showChoice"
            :id="'show-choice-' + _uid"></i>
        <transition name="slidedown">
            <div class="filter-add-choice floating" v-if="showChoice"
                v-dismiss="{switch: 'showChoice', ignore: ['show-choice-' + _uid]}">
                <span v-if="canAddGroups" @click="newGroup" :id="'show-editor-groups-' + _uid">new group</span>
                <span v-if="canAddTerms" @click="newTerm"
                    :id="'show-editor-terms-' + _uid">new term</span>
            </div>
        </transition>
        <transition name="slideright">
            <TermEditor v-if="showEditor" :parent-id="parentId"
                v-dismiss="{switch: 'showEditor', ignore: ['show-editor-groups-' + _uid, 'show-editor-terms-' + _uid]}"></TermEditor>
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
                showChoice: false,
                showEditor: false
            }
        },
        computed:   {
            ...mapGetters('filters', ['getNestLevel']),
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
            ...mapMutations('filters', ['addGroup']),
            newGroup: function () {
                this.showChoice = false;
                this.showEditor = false;
                this.addGroup(this.$parent.filterId);
            },
            newTerm:  function () {
                this.showChoice = false;
                this.showEditor = true;
            }
        }
    }
</script>