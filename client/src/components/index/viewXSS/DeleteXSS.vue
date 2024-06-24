<template>
  <b-modal ref="deleteXSSModal" id="delete-xss-modal" title="Are you sure?" hide-footer>
    <b-form v-on:submit.prevent>
      <div class="text-right">
        <b-button @click="deleteXSS()" variant="outline-danger">Yes, delete this entry</b-button>
        <b-button class="ml-2" @click="$refs.deleteXSSModal.hide()" variant="outline-secondary">Cancel</b-button>
      </div>
    </b-form>
  </b-modal>
</template>
<script>
import axios from "axios";

const basePath = "/api";

export default {
  props: ["to_delete"],
  methods: {
    deleteXSS() {
      const path = `${basePath}/xss/${this.to_delete}`;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success");
          this.$emit("get-xss-list");
          this.$refs.deleteXSSModal.hide();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
  },
};
</script>

<style></style>
