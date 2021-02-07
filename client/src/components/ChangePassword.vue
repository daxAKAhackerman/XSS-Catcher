<template>
  <b-modal
    ref="changePasswordModal"
    id="change-password-modal"
    title="Change password"
    hide-footer
    @hidden="cleanup"
    :visible="$parent.show_password_modal"
  >
    <b-form>
      <b-form-group
        id="input-group-op"
        label="Old password:"
        label-cols="3"
        label-for="input-field-op"
      >
        <b-form-input
          @keyup.enter="changePassword"
          v-model="old_password"
          id="input-field-op"
          type="password"
          required
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-np"
        label="New password:"
        label-cols="3"
        label-for="input-field-np"
      >
        <b-form-input
          @keyup.enter="changePassword"
          v-model="new_password1"
          id="input-field-np"
          type="password"
          required
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-np2"
        label="New password again:"
        label-cols="3"
        label-for="input-field-np2"
      >
        <b-form-input
          @keyup.enter="changePassword"
          v-model="new_password2"
          id="input-field-np2"
          type="password"
          required
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button @click="changePassword" variant="outline-info">Save</b-button>
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
      old_password: "",
      new_password1: "",
      new_password2: "",
    };
  },
  methods: {
    changePassword() {
      const path = basePath + "/user/password";

      const payload = {
        old_password: this.old_password,
        password1: this.new_password1,
        password2: this.new_password2,
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
      this.old_password = "";
      this.new_password1 = "";
      this.new_password2 = "";
      this.$refs.changePasswordModal.hide();
      if (this.$route.name !== "Index") {
        this.$router.push({
          name: "Index",
        });
      }
    },
  },
};
</script>

<style>
</style>
