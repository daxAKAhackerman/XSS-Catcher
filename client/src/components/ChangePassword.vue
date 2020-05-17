<template>
  <b-modal
    ref="changePasswordModal"
    id="change-password-modal"
    title="Change password"
    hide-footer
    @hidden="cleanup"
    :visible="$parent.show_password_modal"
  >
    <b-form @submit="changePassword" @reset="cleanup">
      <b-form-group
        id="input-group-op"
        label="Old password:"
        label-cols="3"
        label-for="input-field-op"
      >
        <b-form-input @keyup.enter="changePassword" v-model="old_password" id="input-field-op" type="password" required></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-np"
        label="New password:"
        label-cols="3"
        label-for="input-field-np"
      >
        <b-form-input @keyup.enter="changePassword" v-model="new_password1" id="input-field-np" type="password" required></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-np2"
        label="New password again:"
        label-cols="3"
        label-for="input-field-np2"
      >
        <b-form-input @keyup.enter="changePassword" v-model="new_password2" id="input-field-np2" type="password" required></b-form-input>
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
      old_password: "",
      new_password1: "",
      new_password2: "",
      show_alert: false,
      alert_msg: ""
    };
  },
  methods: {
    changePassword() {
      const path = basePath + "/user/change_password";

      var payload = new URLSearchParams();

      payload.append("old_password", this.old_password);
      payload.append("password1", this.new_password1);
      payload.append("password2", this.new_password2);

      axios
        .post(path, payload)
        .then(response => {
          void response;
          this.cleanup();
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.show_alert = true;
            this.alert_msg = error.response.data.detail;
          }
        });
    },
    cleanup() {
      this.old_password = "";
      this.new_password1 = "";
      this.new_password2 = "";
      this.show_alert = false;
      this.alert_msg = "";
      this.$refs.changePasswordModal.hide();
      if (this.$route.name !== "Index") {
        this.$router.push({
          name: "Index"
        });
      }
    }
  }
};
</script>

<style>
</style>
