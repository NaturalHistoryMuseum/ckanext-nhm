<script>
import Popup from './Popup.vue';
import { mapState } from 'vuex';
import Copyable from '../misc/Copyable.vue';
import Editable from '../misc/Editable.vue';

export default {
  name: 'BasePopup',
  components: { Popup, Copyable, Editable },
  data: function () {
    return {
      showPopup: false,
    };
  },
  computed: {
    ...mapState('appState', ['status']),
  },
  methods: {
    toggle(event) {
      this.showPopup = event;
    },
  },
};
</script>
