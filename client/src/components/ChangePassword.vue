<template>
  <b-modal
    ref="changePasswordModal"
    id="change-password-modal"
    title="Change password"
    hide-footer
    @hidden="resetCP"
  >
    <b-form
      @submit="changePassword"
      @reset="resetCP"
    >
      <b-form-group
        id="input-group-op"
        label="Old password:"
        label-cols="3"
        label-for="input-field-op"
      >
        <b-form-input
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
          v-model="new_password2"
          id="input-field-np2"
          type="password"
          required
        ></b-form-input>
      </b-form-group>
      <b-button
        type="submit"
        variant="info"
      >Save
      </b-button>
      <b-button type="reset">Cancel</b-button>
    </b-form>
  </b-modal>
</template>

<script>
import axios from 'axios'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  data () {
    return {
      old_password: '',
      new_password1: '',
      new_password2: ''
    }
  },
  methods: {
    changePassword () {
      const path = basePath + '/change_password'

      var payload = new URLSearchParams()

      payload.append('old_password', this.old_password)
      payload.append('password1', this.new_password1)
      payload.append('password2', this.new_password2)

      axios.post(path, payload)
        .then(response => {
          console.log(response.data)
          this.resetCP()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    resetCP () {
      this.old_password = ''
      this.new_password1 = ''
      this.new_password2 = ''
      this.$refs.changePasswordModal.hide()
    }
  }
}
</script>

<style>
</style>
