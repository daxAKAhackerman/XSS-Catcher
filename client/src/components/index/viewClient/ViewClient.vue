<template>
  <b-modal
    ref="viewClientModal"
    id="view-client-modal"
    title="Client"
    hide-footer
    @show="getClient()"
    @hide="cleanup()"
  >
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-name"
        label="Short name:"
        label-cols="3"
        label-for="input-field-name"
      >
        <b-form-input
          @keyup.enter="patchClient"
          v-if="owner_id === user_id || is_admin"
          id="input-field-name"
          v-model="client.name"
        ></b-form-input>
        <b-form-input
          v-else
          readonly
          id="input-field-name"
          v-model="client.name"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-description"
        label="Description:"
        label-cols="3"
        label-for="input-field-description"
      >
        <b-form-input
          @keyup.enter="patchClient"
          v-if="owner_id === user_id || is_admin"
          id="input-field-description"
          v-model="client.description"
        ></b-form-input>
        <b-form-input
          v-else
          readonly
          id="input-field-description"
          v-model="client.description"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-mail"
        label="Send alerts to:"
        label-cols="3"
        label-for="input-field-mail"
      >
        <b-form-input
          @keyup.enter="patchClient"
          v-if="owner_id === user_id || is_admin"
          id="input-field-mail"
          v-model="client.mail_to"
        ></b-form-input>
        <b-form-input
          v-else
          readonly
          id="input-field-mail"
          v-model="client.mail_to"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-owner"
        label="Owner:"
        label-cols="3"
        label-for="input-field-owner"
      >
        <b-form-select
          v-if="is_admin"
          id="input-field-owner"
          v-model="client.owner"
          :options="users_list"
          required
        ></b-form-select>
        <b-form-input
          v-else
          readonly
          id="input-field-owner"
          v-model="client.owner"
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button
          v-if="owner_id === user_id || is_admin"
          @click="patchClient()"
          variant="outline-info"
          >Save</b-button
        >
        <b-button @click="cleanup()" variant="outline-secondary"
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
  props: ["client_id", "is_admin", "owner_id", "user_id"],
  data() {
    return {
      client: {},
      users: {},
    };
  },
  computed: {
    users_list: {
      get() {
        let list = [];
        for (let value of Object.values(this.users)) {
          list.push(value.username);
        }
        return list;
      },
    },
  },
  methods: {
    getClient() {
      const path = basePath + "/client/" + this.client_id;

      axios
        .get(path)
        .then((response) => {
          this.client = response.data;
          this.getUsers();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    patchClient() {
      const path = basePath + "/client/" + this.client_id;

      let owner = "";

      for (let value of Object.values(this.users)) {
        if (value.username === this.client.owner) {
          owner = value.id;
        }
      }

      const payload = {
        name: this.client.name,
        description: this.client.description,
        owner: owner,
      };

      if (this.client.mail_to !== "" && this.client.mail_to !== null) {
        payload.mail_to = this.client.mail_to;
      }

      axios
        .patch(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.cleanup();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    getUsers() {
      const path = basePath + "/user";

      axios
        .get(path)
        .then((response) => {
          this.users = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanup() {
      this.client = {};
      this.$refs.viewClientModal.hide();
      this.$emit("get-clients");
    },
  },
};
</script>

<style></style>
