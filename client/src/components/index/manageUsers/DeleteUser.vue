<template>
  <b-modal
    ref="deleteUserModal"
    id="delete-user-modal"
    title="Are you sure?"
    hide-footer
  >
    <b-form v-on:submit.prevent>
      <div class="text-right">
        <b-button @click="deleteUser()" variant="outline-danger"
          >Yes, delete this user</b-button
        >
        <b-button
          @click="$refs.deleteUserModal.hide()"
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
    deleteUser() {
      const path = `${basePath}/user/${this.to_delete}`;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success");
          this.$refs.deleteUserModal.hide();
          this.$emit("get-users");
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
  },
};
</script>
<style></style>
