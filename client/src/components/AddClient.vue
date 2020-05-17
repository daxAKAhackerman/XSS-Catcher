<template>
  <b-modal
    ref="addClientModal"
    id="add-client-modal"
    title="New client"
    hide-footer
    @hidden="cleanup"
  >
    <b-form @submit="putClient" @reset="cleanup">
      <b-form-group id="input-group-name" label="Name:" label-cols="3" label-for="input-field-name">
        <b-form-input v-model="client.name" id="input-field-name" required></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-description"
        label="Description:"
        label-cols="3"
        label-for="input-field-description"
      >
        <b-form-input v-model="client.description" id="input-field-description" required></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button type="submit" variant="outline-info">Save</b-button>
        <b-button type="reset" variant="outline-secondary">Cancel</b-button>
      </div>
    </b-form>
    <br v-if="show_alert" />
    <b-alert show variant="danger" v-if="show_alert">{{ alert_msg }}</b-alert>
  </b-modal>
</template>

<script>
import axios from "axios";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  data() {
    return {
      client: {},
      show_alert: false,
      alert_msg: ""
    };
  },
  methods: {
    putClient() {
      const path = basePath + "/client";

      var payload = new URLSearchParams();

      payload.append("name", this.client.name);
      payload.append("description", this.client.description);

      axios
        .put(path, payload)
        .then(response => {
          void response;
          this.cleanup();
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.alert_msg = error.response.data.detail;
            this.show_alert = true;
          }
        });
    },
    cleanup() {
      this.client = {};
      this.show_alert = false;
      this.alert_msg = "";
      this.$refs.addClientModal.hide();
      this.$parent.getClients();
    }
  }
};
</script>

<style>
</style>
