<template>
  <b-modal
    ref="createUserModal"
    id="create-user-modal"
    title="Create user"
    hide-footer
    @hide="cleanup()"
  >
    <b-form>
      <b-form-group
        id="input-group-username"
        label="Username:"
        label-cols="3"
        label-for="input-field-username"
      >
        <b-form-input
          @keyup.enter="createUser"
          v-model="username"
          id="input-field-username"
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button @click="createUser()" variant="outline-info"
          >Create user</b-button
        >
        <b-button @click="cleanup()" variant="outline-secondary"
          >Cancel</b-button
        >
      </div>
    </b-form>

    <ViewPassword
      :username="username"
      :password="data.detail"
      @cleanup="cleanup()"
    />
  </b-modal>
</template>

<script>
import axios from "axios";

import ViewPassword from "./ViewPassword";

const basePath = "/api";

export default {
  components: {
    ViewPassword,
  },
  data() {
    return {
      data: {},
      username: "",
    };
  },
  methods: {
    createUser() {
      const path = basePath + "/user";

      const payload = {
        username: this.username,
      };

      axios
        .post(path, payload)
        .then((response) => {
          this.data = response.data;
          this.$bvModal.show("view-password-modal");
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanup() {
      this.data = {};
      this.username = "";
      this.$refs.createUserModal.hide();
      this.$emit("get-users");
    },
  },
};
</script>

<style></style>
