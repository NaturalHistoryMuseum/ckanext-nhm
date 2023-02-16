<template>
  <div
    class="filter-fields fields"
    :class="fieldsClasses"
    @click="toggleShowFields"
    :id="'fields-dropdown-' + _uid"
  >
    <span>{{ fieldsPlaceholder }}</span>
    <transition name="slidedown">
      <div
        v-if="showFields"
        class="floating"
        v-dismiss="{
          switch: 'showFields',
          ignore: ['#fields-dropdown-' + _uid],
        }"
      >
        <span
          class="fields"
          v-for="field in fields || []"
          v-bind:key="field.id"
          >{{ field }}</span
        >
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'FieldsDropdown',
  data: function () {
    return {
      showFields: false,
    };
  },
  props: ['fields'],
  computed: {
    fieldsClasses() {
      let fieldsClasses = this.showFields ? ['expanded'] : [];
      if (this.fields !== undefined && this.fields.length > 1) {
        fieldsClasses.push('expandable');
      }
      return fieldsClasses;
    },
    fieldsPlaceholder() {
      let numFields = this.fields.length;
      if (numFields === 0) {
        return '*';
      } else if (numFields === 1) {
        return this.fields[0];
      } else {
        return numFields + ' fields';
      }
    },
  },
  methods: {
    toggleShowFields() {
      this.showFields = this.fields.length > 1 ? !this.showFields : false;
    },
  },
};
</script>
