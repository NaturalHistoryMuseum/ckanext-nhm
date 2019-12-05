<template>
    <p class="copyable" :class="{'copied': copySuccess, 'copy-failed': copyFailure}">
        <slot></slot>
        <button v-clipboard:copy="copyText"
                v-clipboard:success="onCopySuccess"
                v-clipboard:error="onCopyError">
            <i class="fas" :class="{'fa-check': copySuccess, 'fa-times': copyFailure, 'fa-clipboard': !copyAttempt}"></i></button>
    </p>
</template>

<script>
    export default {
        name:     'Copyable',
        data:     function () {
            return {
                copySuccess: false,
                copyAttempt: false
            }
        },
        props:    ['copyText'],
        computed: {
            copyFailure() {
                return (!this.copySuccess) && this.copyAttempt;
            }
        },
        methods:  {
            onCopySuccess() {
                this.copySuccess = true;
                this.copyAttempt = true;
            },
            onCopyError() {
                this.copySuccess = false;
                this.copyAttempt = true;
            }
        }
    }
</script>