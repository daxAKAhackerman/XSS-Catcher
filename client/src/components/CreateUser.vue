<template>

  <b-modal
    ref="createUserModal"
    id="create-user-modal"
    title="Create user"
    hide-footer
    @hide="cleanup"
  >
    <b-form @submit="createUser">

      <b-form-group
        id="input-group-username"
        label="Username:"
        label-cols="3"
        label-for="input-field-username"
      >
        <b-form-input
          v-model="username"
          id="input-field-username"
        ></b-form-input>
      </b-form-group>
      <b-button type="submit" variant="info">Create user</b-button>
    </b-form>
    <br />
    <b-alert
      show
      variant="danger"
      v-if="show_alert"
    >{{ alert_msg }}</b-alert>
    <b-modal
      ref="viewPasswordModal"
      id="view-password-modal"
      title="User created"
      hide-footer
      @hide="$refs.createUserModal.hide()"
    >
      <p>Username: {{ username }}</p>
      <p>Password: {{ data.detail }}</p>
    </b-modal>
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
      data: {},
      username: '',
      show_alert: false,
      alert_msg: ''
    }
  },
  methods: {
    createUser () {
      const path = basePath + '/user/new'

      var payload = new URLSearchParams()

      payload.append('username', this.username)

      axios.post(path, payload)
        .then(response => {
          this.data = response.data
          this.$refs.viewPasswordModal.show()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            this.show_alert = true
            this.alert_msg = error.response.data.detail
          }
        })
    },
    cleanup () {
      this.data = {}
      this.username = ''
      this.show_alert = false
      this.alert_msg = ''
    }
  }
}

</script>

<style></style>
