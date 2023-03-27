<template>
  <Popup
    classes="help-popup"
    icon="fa-question-circle inline-icon-left"
    :label="label"
    :popup-id="popupId"
    :parent-toggle="showPopup"
    v-on:toggle="toggle"
    :is-button="false"
  >
    <slot></slot>
  </Popup>
</template>

<script>
import BasePopup from './BasePopup.vue';

export default {
  name: 'Help',
  extends: BasePopup,
  props: ['popupId', 'label'],
};
</script>
