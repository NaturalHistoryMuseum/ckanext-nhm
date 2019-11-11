<template>
    <div class="filter-add">
        <i class="fas fa-plus-square fa-lg" @click="showChoice = !showChoice"></i>
        <transition name="slidedown">
            <div class="filter-add-choice floating" v-if="showChoice">
                <span v-if="addGroups" @click="newGroup">new group</span>
                <span v-if="addTerms" @click="newTerm">new term</span>
            </div>
        </transition>
        <transition name="slideright">
            <TermEditor v-if="showEditor" v-bind:resource-ids="resourceIds"
                v-bind:schema="schema"></TermEditor>
        </transition>
    </div>
</template>

<script>
    import TermEditor from './TermEditor.vue';

    export default {
        name:       'FilterAdd',
        components: {
            TermEditor
        },
        props:      ['schema', 'isGroup', 'siblings', 'nestLevel', 'resourceIds'],
        data:       function () {
            return {
                showChoice: false,
                showEditor: false
            }
        },
        computed:   {
            addGroups: function () {
                return this.isGroup ? this.nestLevel === 0 : false;
            },
            addTerms:  function () {
                return this.isGroup ? this.siblings.length < 10 : false;
            }
        },
        methods:    {
            newGroup: function () {
                this.showChoice = false;
                this.showEditor = false;
                this.siblings.push({
                                       'and': []
                                   });
            },
            newTerm:  function () {
                this.showChoice = false;
                this.showEditor = true;
            }
        }
    }
</script>