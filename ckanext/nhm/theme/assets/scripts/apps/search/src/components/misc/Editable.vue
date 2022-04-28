<template>
    <p class="editable">
        <input v-model="value">
        <button aria-label="edit button" @click="onSave" :class="{edited: hasChanged}" title="save changes">
            <i class="fas" :class="{'fa-check': editSuccess, 'fa-times': editFailure, 'fa-save': !editAttempt}"></i>
        </button>
    </p>
</template>

<script>
    export default {
        name:     'Editable',
        data:     function () {
            return {
                editAttempt: false,
                value: this.editText
            }
        },
        props: ['editText', 'editStatus'],
        computed: {
            editFailure() {
                return this.editStatus.failed && this.editAttempt;
            },
            editSuccess() {
                return (!this.editStatus.failed) && this.editAttempt;
            },
            hasChanged() {
                return this.value !== this.editText;
            }
        },
        methods:  {
            onSave() {
                this.editAttempt = true;
                this.$emit('save', this.value);
                setTimeout(() => {
                    this.editAttempt = false;
                }, 2000)
            }
        }
    }
</script>