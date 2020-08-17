<template>
  <b-modal
    ref="settingsModal"
    id="settings-modal"
    title="Settings"
    hide-footer
    size="md"
    @show="getSettings"
    @hide="cleanup"
  >
    <h3>SMTP settings</h3>
    <hr />
    <b-form @submit="postSettings" @reset="cleanup">
      <b-form-group
        id="input-group-host"
        label="SMTP server: "
        label-cols="3"
        label-for="input-field-host"
      >
        <b-form-input id="input-field-host" v-model="settings.smtp_host"></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-port"
        label="SMTP port: "
        label-cols="3"
        label-for="input-field-port"
      >
        <b-form-input type="number" id="input-field-port" v-model="settings.smtp_port"></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-mail_from"
        label="Sender address: "
        label-cols="3"
        label-for="input-field-mail_from"
      >
        <b-form-input id="input-field-mail_from" v-model="settings.mail_from"></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-user"
        label="Username: "
        label-cols="3"
        label-for="input-field-user"
      >
        <b-form-input id="input-field-user" v-model="settings.smtp_user"></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-pass"
        label="Password: "
        label-cols="3"
        label-for="input-field-pass"
      >
        <b-form-input
          type="password"
          id="input-field-pass"
          v-model="settings.smtp_pass"
          placeholder="LEAVE UNCHANGED TO KEEP SAVED PASSWORD"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-starttls"
        label="STARTTLS: "
        label-cols="3"
        label-for="input-field-starttls"
      >
        <b-form-checkbox
          style="margin-top:13px"
          @change="settings.ssl_tls = false"
          v-model="settings.starttls"
          id="input-field-starttls"
        ></b-form-checkbox>
      </b-form-group>

      <b-form-group
        id="input-group-ssl_tls"
        label="SSL/TLS: "
        label-cols="3"
        label-for="input-field-ssl_tls"
      >
        <b-form-checkbox
          style="margin-top:13px"
          @change="settings.starttls = false"
          v-model="settings.ssl_tls"
          id="input-field-ssl_tls"
        ></b-form-checkbox>
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
      settings: {},
      show_alert: false,
      alert_msg: "",
      alert_type: "danger",
    };
  },
  methods: {
    getSettings() {
      const path = basePath + "/settings";

      axios
        .get(path)
        .then((response) => {
          this.settings = response.data;
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    postSettings() {
      const path = basePath + "/settings";

      var payload = new URLSearchParams();

      if (this.settings.smtp_host !== "") {
        payload.append("mail_from", this.settings.mail_from);
        payload.append("smtp_host", this.settings.smtp_host);
        payload.append("smtp_port", this.settings.smtp_port);

        if (this.settings.smtp_user !== "") {
          payload.append("smtp_user", this.settings.smtp_user);
        }

        if (this.settings.smtp_pass !== undefined) {
          payload.append("smtp_pass", this.settings.smtp_pass);
        }

        if (this.settings.ssl_tls) {
          payload.append("ssl_tls", 1);
        } else if (this.settings.starttls) {
          payload.append("starttls", 1);
        }
      }
      axios
        .post(path, payload)
        .then((response) => {
          void response;
          this.cleanup();
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.alert_msg = error.response.data.detail;
            this.show_alert = true;
          }
        });
    },
    cleanup() {
      this.$refs.settingsModal.hide();
      this.show_alert = false;
      this.alert_msg = "";
      this.settings = {};
    },
  },
};
</script>

<style></style>
