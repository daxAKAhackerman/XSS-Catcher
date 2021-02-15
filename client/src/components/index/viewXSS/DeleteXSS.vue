<template>
  <b-modal
    ref="deleteXSSModal"
    id="delete-xss-modal"
    title="Are you sure?"
    hide-footer
  >
    <b-form>
      <b-button @click="deleteXSS" variant="outline-danger"
        >Yes, delete this entry</b-button
      >
      <b-button @click="$refs.deleteXSSModal.hide()" variant="outline-secondary"
        >Cancel</b-button
      >
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
      const path = basePath + "/xss/" + this.to_delete;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
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
