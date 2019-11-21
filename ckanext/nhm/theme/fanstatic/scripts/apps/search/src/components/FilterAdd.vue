<template>
    <div class="filter-add">
        <i class="fas fa-plus-square fa-lg" @click="showChoice = !showChoice"></i>
        <transition name="slidedown">
            <div class="filter-add-choice floating" v-if="showChoice">
                <span v-if="canAddGroups" @click="newGroup">new group</span>
                <span v-if="canAddTerms" @click="newTerm">new term</span>
            </div>
        </transition>
        <transition name="slideright">
            <TermEditor v-if="showEditor" :parent-id="parentId"></TermEditor>
        </transition>
    </div>
</template>

<script>
    import Loading from './Loading.vue';
    import LoadError from './LoadError.vue';
    const TermEditor = import('./TermEditor.vue');
    import {mapState, mapGetters, mapMutations} from 'vuex';

    export default {
        name:       'FilterAdd',
        props: ['parentId'],
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
            canAddTerms: function () {
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