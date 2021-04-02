<template>
  <b-modal
    ref="settingsModal"
    id="settings-modal"
    title="Settings"
    hide-footer
    size="lg"
    @show="getSettings()"
    @hide="cleanup()"
  >
    <h3>SMTP settings</h3>
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-host"
        label="SMTP server: "
        label-cols="3"
        label-for="input-field-host"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          id="input-field-host"
          v-model="settings.smtp_host"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-port"
        label="SMTP port: "
        label-cols="3"
        label-for="input-field-port"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          type="number"
          id="input-field-port"
          v-model="settings.smtp_port"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-mail_from"
        label="Sender address: "
        label-cols="3"
        label-for="input-field-mail_from"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          id="input-field-mail_from"
          v-model="settings.mail_from"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-mail_to"
        label="Default recipient: "
        label-cols="3"
        label-for="input-field-mail_to"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          id="input-field-mail_to"
          v-model="settings.mail_to"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-user"
        label="Username: "
        label-cols="3"
        label-for="input-field-user"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          id="input-field-user"
          v-model="settings.smtp_user"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-pass"
        label="Password: "
        label-cols="3"
        label-for="input-field-pass"
      >
        <b-form-input
          @keyup.enter="patchSettings"
          type="password"
          id="input-field-pass"
          v-model="settings.smtp_pass"
          placeholder="Leave unchanged to keep saved password"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-starttls"
        label="STARTTLS: "
        label-cols="3"
        label-for="input-field-starttls"
      >
        <b-form-checkbox
          style="margin-top: 13px"
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
          style="margin-top: 13px"
          @change="settings.starttls = false"
          v-model="settings.ssl_tls"
          id="input-field-ssl_tls"
        ></b-form-checkbox>
      </b-form-group>
      <b-form-group
        id="input-group-status"
        label="SMTP status: "
        label-cols="3"
        label-for="input-field-status"
      >
        <p
          v-if="settings.smtp_status === null"
          style="margin-top: 13px; color: #f89406"
          id="input-field-status"
        >
          <b>NOT CONFIGURED OR NOT TESTED</b>
        </p>
        <p
          v-else-if="settings.smtp_status === true"
          style="margin-top: 13px; color: #62c462"
          id="input-field-status"
        >
          <b>OK</b>
        </p>
        <p
          v-else-if="settings.smtp_status === false"
          style="margin-top: 13px; color: #ee5f5b"
          id="input-field-status"
        >
          <b>BAD CONFIGURATION</b>
        </p>
      </b-form-group>
    </b-form>
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-smtp_test"
        label="SMTP test"
        label-cols="3"
        label-for="input-field-smtp_test"
      >
        <b-input-group>
          <b-form-input
            @keyup.enter="testSettings"
            v-model="smtp_test_mail_to"
            id="input-field-smtp_test"
            placeholder="Recipient"
          ></b-form-input>
          <b-input-group-append>
            <b-button @click="testSettings" variant="outline-warning"
              >Test</b-button
            >
          </b-input-group-append>
        </b-input-group>
      </b-form-group>
    </b-form>
    <hr />
    <h3>Webhook settings</h3>
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-webhook"
        label="Default webhook URL: "
        label-cols="3"
        label-for="input-field-webhook"
        ><b-input-group>
          <b-form-input
            @keyup.enter="patchSettings"
            id="input-field-webhook"
            v-model="settings.webhook_url"
          ></b-form-input>
          <b-input-group-append>
            <b-button @click="testWebhook" variant="outline-warning"
              >Test</b-button
            >
          </b-input-group-append>
        </b-input-group>
      </b-form-group>
    </b-form>
    <div class="text-right">
      <b-button @click="patchSettings()" variant="outline-info">Save</b-button>
      <b-button @click="cleanup()" variant="outline-secondary">Cancel</b-button>
    </div>
  </b-modal>
</template>

<script>
import axios from "axios";

const basePath = "/api";

export default {
  data() {
    return {
      settings: {},
      smtp_test_mail_to: "",
    };
  },
  methods: {
    getSettings() {
      const path = `${basePath}/settings`;

      axios
        .get(path)
        .then((response) => {
          this.settings = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    patchSettings() {
      const path = `${basePath}/settings`;

      const payload = {};

      if (this.settings.smtp_host !== "" && this.settings.smtp_host !== null) {
        payload.mail_from = this.settings.mail_from;
        payload.smtp_host = this.settings.smtp_host;
        payload.smtp_port = this.settings.smtp_port;

        if (
          this.settings.smtp_user !== "" &&
          this.settings.smtp_user !== null
        ) {
          payload.smtp_user = this.settings.smtp_user;
        }

        if (
          this.settings.smtp_pass !== undefined &&
          this.settings.smtp_pass !== null
        ) {
          payload.smtp_pass = this.settings.smtp_pass;
        }

        if (this.settings.ssl_tls) {
          payload.ssl_tls = 1;
        } else if (this.settings.starttls) {
          payload.starttls = 1;
        }
      }

      if (
        this.settings.webhook_url !== "" &&
        this.settings.webhook_url !== null
      ) {
        payload.webhook_url = this.settings.webhook_url;
      }

      if (this.settings.mail_to !== "" && this.settings.mail_to !== null) {
        payload.mail_to = this.settings.mail_to;
      }

      axios
        .patch(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.getSettings();
        })
        .catch((error) => {
          this.handleError(error);
          this.getSettings();
        });
    },
    testSettings() {
      const path = `${basePath}/settings/smtp_test`;

      const payload = {
        mail_to: this.smtp_test_mail_to,
      };

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.getSettings();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    testWebhook() {
      const path = `${basePath}/settings/webhook_test`;

      const payload = {
        webhook_url: this.settings.webhook_url,
      };

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanup() {
      this.$refs.settingsModal.hide();
      this.settings = {};
    },
  },
};
</script>

<style></style>
