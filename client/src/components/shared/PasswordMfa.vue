<template>
  <b-modal ref="passwordMfaModal" id="password-mfa-modal" title="Password and MFA" hide-footer @hidden="cleanup()"
    @show="showApiKeysSection && listApiKeys()" :visible="show_password_modal">
    <h4>Change password</h4>
    <br />
    <b-form v-on:submit.prevent>
      <b-form-group id="input-group-op" label="Old password:" label-cols="3" label-for="input-field-op">
        <b-form-input @keyup.enter="changePassword()" v-model="old_password" id="input-field-op" type="password"
          required></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-np" label="New password:" label-cols="3" label-for="input-field-np">
        <b-form-input @keyup.enter="changePassword()" v-model="new_password1" id="input-field-np" type="password"
          required></b-form-input>
      </b-form-group>

      <b-form-group id="input-group-np2" label="New password again:" label-cols="3" label-for="input-field-np2">
        <b-form-input @keyup.enter="changePassword()" v-model="new_password2" id="input-field-np2" type="password"
          required></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button @click="changePassword()" variant="outline-info">Save</b-button>
        <b-button @click="cleanup()" variant="outline-secondary">Cancel</b-button>
      </div>
    </b-form>
    <div v-if="show_mfa_section">
      <hr />
      <h4>Multi Factor Authentication</h4>
      <br />
      <b-button v-if="mfa_set" @click="unsetMfa()" block variant="outline-danger">Disable MFA</b-button>
      <b-button v-else @click="generateMfaQrCode()" block variant="outline-success">Generate MFA QR code</b-button>
      <div v-if="show_mfa_form">
        <br />
        <b-form v-on:submit.prevent>
          <b-img center :src="qr_code"></b-img>
          <div class="text-center">
            <p>{{ mfa_secret }}</p>
          </div>
          <b-form-group id="input-group-otp" label="OTP:" label-cols="3" label-for="input-field-otp">
            <b-form-input @keyup.enter="setMfa()" v-model="otp" id="input-field-otp" autocomplete="off"
              required></b-form-input>
          </b-form-group>

          <div class="text-right">
            <b-button @click="setMfa()" variant="outline-info">Save</b-button>
            <b-button @click="cleanup()" variant="outline-secondary">Cancel</b-button>
          </div>
        </b-form>
      </div>
    </div>
    <div v-if="showApiKeysSection">
      <hr />
      <h4>API keys</h4>
      <br />
      <ApiKeysTable :apiKeys="apiKeys" @list-api-keys="listApiKeys()" />
      <ShowApiKey :apiKey="newApiKey" @list-api-keys="listApiKeys()" @cleanup-new-api-key="newApiKey = ''"/>
      <b-button block variant="outline-success" @click="createApiKey()" v-b-tooltip.hover
        title="You can generate a maximum of 5 API keys">Generate API key</b-button>
    </div>
  </b-modal>
</template>

<script>
import axios from "axios"

import ApiKeysTable from "../index/security/ApiKeysTable"
import ShowApiKey from "../index/security/ShowApiKey"

const basePath = "/api"

export default {
  props: ["show_password_modal", "mfa_set", "user_id", "show_mfa_section", "showApiKeysSection"],
  components: {
    ApiKeysTable,
    ShowApiKey
  },
  data() {
    return {
      old_password: "",
      new_password1: "",
      new_password2: "",
      show_mfa_form: false,
      mfa_secret: "",
      mfa_qr_code_base64: "",
      otp: "",
      apiKeys: [],
      newApiKey: "",
    }
  },
  computed: {
    qr_code: function () {
      return `data:image/png;base64,${this.mfa_qr_code_base64}`
    },
  },
  methods: {
    changePassword() {
      const path = `${basePath}/user/password`

      const payload = {
        old_password: this.old_password,
        password1: this.new_password1,
        password2: this.new_password2,
      }

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.cleanup()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    generateMfaQrCode() {
      const path = `${basePath}/user/mfa`

      axios
        .get(path)
        .then((response) => {
          this.mfa_secret = response.data.secret
          this.mfa_qr_code_base64 = response.data.qr_code
          this.show_mfa_form = true
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    setMfa() {
      const path = `${basePath}/user/mfa`

      const payload = {
        secret: this.mfa_secret,
        otp: this.otp,
      }

      axios
        .post(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.cleanup()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    unsetMfa() {
      const path = `${basePath}/user/${this.user_id}/mfa`

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.cleanup()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    listApiKeys() {
      const path = `${basePath}/user/${this.user_id}/apikey`

      axios
        .get(path)
        .then((response) => {
          this.apiKeys = response.data
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    createApiKey() {
      const path = `${basePath}/user/apikey`

      axios
        .post(path)
        .then((response) => {
          this.newApiKey = response.data.key
          this.$bvModal.show("show-api-key-modal")
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    cleanup() {
      this.$refs.passwordMfaModal.hide()
      this.old_password = ""
      this.new_password1 = ""
      this.new_password2 = ""
      this.show_mfa_form = false
      this.mfa_secret = ""
      this.mfa_qr_code_base64 = ""
      this.otp = ""
      this.$emit("get-user")
      if (this.$route.name !== "Index") {
        this.$router.push({
          name: "Index",
        })
      }
    },
  },
}
</script>

<style>

</style>
