<template>
  <b-modal
    ref="deleteClientModal"
    id="delete-client-modal"
    title="Are you sure?"
    hide-footer
  >
    <b-form v-on:submit.prevent>
      <div class="text-right">
        <b-button @click="deleteClient" variant="outline-danger"
          >Yes, delete this entry</b-button
        >
        <b-button
          @click="$refs.deleteClientModal.hide()"
          variant="outline-secondary"
          >Cancel</b-button
        >
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
    deleteClient() {
      const path = `${basePath}/client/${this.to_delete}`;
      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success");
          this.$emit("get-clients");
          this.$refs.deleteClientModal.hide();
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
