<template>
  <p
    class="copyable"
    :class="{ copied: copySuccess, 'copy-failed': copyFailure }"
  >
    <slot></slot>
    <button
      v-clipboard:copy="copyText"
      v-clipboard:success="onCopySuccess"
      v-clipboard:error="onCopyError"
      aria-label="copy button"
      title="copy this"
    >
      <i
        class="fas"
        :class="{
          'fa-check': copySuccess && copyAttempt,
          'fa-times': copyFailure,
          'fa-clipboard': !copyAttempt,
        }"
      ></i>
    </button>
    <button
      aria-label="edit button"
      v-if="editButton"
      @click="$emit('edit')"
      title="edit this"
    >
      <i class="fas fa-pencil-alt"></i>
    </button>
  </p>
</template>

<script>
export default {
  name: 'Copyable',
  data: function () {
    return {
      copySuccess: false,
      copyAttempt: false,
    };
  },
  props: {
    copyText: {},
    editButton: {
      default: false,
    },
  },
  computed: {
    copyFailure() {
      return !this.copySuccess && this.copyAttempt;
    },
  },
  methods: {
    onCopySuccess() {
      this.copySuccess = true;
      this.copyAttempt = true;
      setTimeout(() => {
        this.copyAttempt = false;
      }, 2000);
    },
    onCopyError() {
      this.copySuccess = false;
      this.copyAttempt = true;
      setTimeout(() => {
        this.copyAttempt = false;
      }, 2000);
    },
  },
};
</script>
