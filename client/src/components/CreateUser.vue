<template>

  <b-modal
    ref="createUserModal"
    id="create-user-modal"
    title="Create user"
    hide-footer
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
    <b-modal
      ref="viewPasswordModal"
      id="view-password-modal"
      title="User created"
      hide-footer
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
      username: ''
    }
  },
  methods: {
    createUser () {
      const path = basePath + '/register'

      var payload = new URLSearchParams()

      payload.append('username', this.username)

      axios.post(path, payload)
        .then(response => {
          this.data = response.data
          this.$refs.viewPasswordModal.show()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    }

  }
}

</script>

<style></style>
