<template>
  <b-modal ref="settingsModal" id="settings-modal" title="Settings" hide-footer size="lg" @show="getSettings()"
    @hide="cleanup()">
    <h3>SMTP settings</h3>
    <b-form v-on:submit.prevent>
      <b-form-group id="input-group-host" label="SMTP server: " label-cols="3" label-for="input-field-host">
        <b-form-input @keyup.enter="patchSettings" id="input-field-host" v-model="settings.smtp_host"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-port" label="SMTP port: " label-cols="3" label-for="input-field-port">
        <b-form-input @keyup.enter="patchSettings" type="number" id="input-field-port"
          v-model="settings.smtp_port"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-mail_from" label="Sender address: " label-cols="3"
        label-for="input-field-mail_from">
        <b-form-input @keyup.enter="patchSettings" id="input-field-mail_from"
          v-model="settings.mail_from"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-mail_to" label="Default recipient: " label-cols="3" label-for="input-field-mail_to">
        <b-form-input @keyup.enter="patchSettings" id="input-field-mail_to" v-model="settings.mail_to"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-user" label="Username: " label-cols="3" label-for="input-field-user">
        <b-form-input @keyup.enter="patchSettings" id="input-field-user" v-model="settings.smtp_user"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-pass" label="Password: " label-cols="3" label-for="input-field-pass">
        <b-form-input @keyup.enter="patchSettings" type="password" id="input-field-pass" v-model="settings.smtp_pass"
          placeholder="Leave unchanged to keep saved password"></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-starttls" label="STARTTLS: " label-cols="3" label-for="input-field-starttls">
        <b-form-checkbox style="margin-top: 13px" @change="settings.ssl_tls = false" v-model="settings.starttls"
          id="input-field-starttls"></b-form-checkbox>
      </b-form-group>

      <b-form-group id="input-group-ssl_tls" label="SSL/TLS: " label-cols="3" label-for="input-field-ssl_tls">
        <b-form-checkbox style="margin-top: 13px" @change="settings.starttls = false" v-model="settings.ssl_tls"
          id="input-field-ssl_tls"></b-form-checkbox>
      </b-form-group>
      <b-form-group id="input-group-status" label="SMTP status: " label-cols="3" label-for="input-field-status">
        <p v-if="settings.smtp_status === null" class="new-config" id="input-field-status">
          <b>NOT CONFIGURED OR NOT TESTED</b>
        </p>
        <p v-else-if="settings.smtp_status === true" class="good-config" id="input-field-status">
          <b>OK</b>
        </p>
        <p v-else-if="settings.smtp_status === false" class="bad-config" id="input-field-status">
          <b>BAD CONFIGURATION</b>
        </p>
      </b-form-group>
    </b-form>
    <b-form v-on:submit.prevent>
      <b-form-group id="input-group-smtp_test" label="SMTP test" label-cols="3" label-for="input-field-smtp_test">
        <b-input-group>
          <b-form-input @keyup.enter="testSettings()" v-model="smtp_test_mail_to" id="input-field-smtp_test"
            placeholder="Recipient"></b-form-input>
          <b-input-group-append>
            <b-button v-b-tooltip.hover title="Don't forget to save before testing!" @click="testSettings()"
              variant="outline-warning">Test</b-button>
          </b-input-group-append>
        </b-input-group>
      </b-form-group>
    </b-form>
    <hr />
    <h3>Webhook settings</h3>
    <b-form v-on:submit.prevent>
      <b-form-group id="input-group-webhook-type" label="Webhook format: " label-cols="3"
        label-for="input-field-webhook-type">
        <b-form-radio-group id="input-field-webhook-type" v-model="settings.webhook_type" :options="webhook_types_radio"
          block buttons button-variant="outline-primary"></b-form-radio-group>
      </b-form-group>
      <b-form-group id="input-group-webhook" label="Default webhook URL: " label-cols="3"
        label-for="input-field-webhook"><b-input-group>
          <b-form-input @keyup.enter="patchSettings()" id="input-field-webhook"
            v-model="settings.webhook_url"></b-form-input>
          <b-input-group-append>
            <b-button v-b-tooltip.hover title="Don't forget to save before testing!" @click="testWebhook()"
              variant="outline-warning">Test</b-button>
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
import axios from "axios"

const basePath = "/api"

export default {
  data() {
    return {
      settings: {},
      smtp_test_mail_to: "",
      webhook_types_radio: [
        { text: "Slack", value: 0 },
        { text: "Discord", value: 1 },
        { text: "Automation", value: 2 },
      ],
    }
  },
  methods: {
    getSettings() {
      const path = `${basePath}/settings`

      axios
        .get(path)
        .then((response) => {
          this.settings = response.data
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    patchSettings() {
      const path = `${basePath}/settings`

      const payload = {}

      if (this.settings.smtp_host !== undefined) {
        payload.smtp_host = this.settings.smtp_host
      }

      if (this.settings.smtp_port !== undefined) {
        payload.smtp_port = this.settings.smtp_port
      }

      if (this.settings.mail_from !== undefined) {
        payload.mail_from = this.settings.mail_from
      }

      if (this.settings.mail_to !== undefined) {
        payload.mail_to = this.settings.mail_to
      }

      if (this.settings.smtp_user !== undefined) {
        payload.smtp_user = this.settings.smtp_user
      }

      if (this.settings.smtp_pass !== undefined) {
        payload.smtp_pass = this.settings.smtp_pass
      }

      if (this.settings.webhook_url !== undefined) {
        payload.webhook_url = this.settings.webhook_url
      }

      payload.webhook_type = this.settings.webhook_type
      payload.starttls = this.settings.starttls
      payload.ssl_tls = this.settings.ssl_tls

      axios
        .patch(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.getSettings()
        })
        .catch((error) => {
          this.handleError(error)
          this.getSettings()
        })
    },
    testSettings() {
      const path = `${basePath}/settings/smtp_test`

      const payload = {
        mail_to: this.smtp_test_mail_to,
      }

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.getSettings()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    testWebhook() {
      const path = `${basePath}/settings/webhook_test`

      const payload = {
        webhook_url: this.settings.webhook_url,
      }

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    cleanup() {
      this.$refs.settingsModal.hide()
      this.settings = {}
    },
  },
}
</script>

<style>
.new-config {
  margin-top: 13px;
  color: #f89406;
}

.good-config {
  margin-top: 13px;
  color: #62c462;
}

.bad-config {
  margin-top: 13px;
  color: #ee5f5b;
}
</style>
