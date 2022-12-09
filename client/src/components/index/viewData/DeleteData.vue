<template>
  <b-modal
    ref="deleteDataModal"
    id="delete-data-modal"
    title="Are you sure?"
    hide-footer
  >
    <b-form v-on:submit.prevent>
      <b-button @click="deleteData()" variant="outline-danger"
        >Yes, delete this entry</b-button
      >
      <b-button
        @click="$refs.deleteDataModal.hide()"
        variant="outline-secondary"
        >Cancel</b-button
      >
    </b-form>
  </b-modal>
</template>
<script>
import axios from "axios";

const basePath = "/api";

export default {
  props: ["to_delete", "to_delete_type"],
  methods: {
    deleteData() {
      const path = `${basePath}/xss/${this.to_delete}/data/${this.to_delete_type}`;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success");
          this.$emit("get-data");
          this.$refs.deleteDataModal.hide();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
  },
};
</script>

<style>
</style>
