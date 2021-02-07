<template>
  <b-modal
    ref="addClientModal"
    id="add-client-modal"
    title="New client"
    hide-footer
    @hidden="cleanup"
  >
    <b-form>
      <b-form-group
        id="input-group-name"
        label="Name:"
        label-cols="3"
        label-for="input-field-name"
      >
        <b-form-input
          @keyup.enter="postClient"
          v-model="client.name"
          id="input-field-name"
          required
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-description"
        label="Description:"
        label-cols="3"
        label-for="input-field-description"
      >
        <b-form-input
          @keyup.enter="postClient"
          v-model="client.description"
          id="input-field-description"
          required
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button @click="postClient" variant="outline-info">Save</b-button>
        <b-button @click="cleanup" variant="outline-secondary">Cancel</b-button>
      </div>
    </b-form>
  </b-modal>
</template>

<script>
import axios from "axios";

const basePath = "/api";

export default {
  data() {
    return {
      client: {
        name: "",
        description: "",
      },
    };
  },
  methods: {
    postClient() {
      const path = basePath + "/client";

      const payload = {
        name: this.client.name,
        description: this.client.description,
      };

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.cleanup();
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    makeToast(message, variant, title) {
      this.$root.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: variant,
      });
    },
    cleanup() {
      this.client = {
        name: "",
        description: "",
      };
      this.$refs.addClientModal.hide();
      this.$parent.getClients();
    },
  },
};
</script>

<style>
</style>
