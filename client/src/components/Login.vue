<template>
  <b-container>
    <b-row align-v="center">
      <b-col
        md="4"
        offset-sm="4"
      >
        <b-card>
          <b-form @submit="postLogin">
            <b-form-group
              id="input-group-username"
              label="Username:"
              label-for="input-field-username"
            >
              <b-form-input
                id="input-field-username"
                v-model="form.username"
                required
                placeholder="Enter username"
              ></b-form-input>
            </b-form-group>
            <b-form-group
              id="input-group-password"
              label="Password:"
              label-for="input-field-password"
            >
              <b-form-input
                type="password"
                id="input-field-password"
                v-model="form.password"
                required
                placeholder="Enter password"
              ></b-form-input>
            </b-form-group>
            <b-form-group id="input-group-remember">
              <b-form-checkbox-group
                v-model="form.remember"
                id="input-field-remember"
              >
                <b-form-checkbox v-model="form.remember">Remember me:</b-form-checkbox>
              </b-form-checkbox-group>
            </b-form-group>
            <b-button
              type="submit"
              variant="info"
            >Login</b-button>
          </b-form>
          <b-alert
            show
            variant="danger"
            v-if="show_alert"
          >Bad login</b-alert>
        </b-card>
      </b-col>
    </b-row>
    <ChangePasswordLogin />
  </b-container>
</template>

<script>
import axios from 'axios'

import ChangePasswordLogin from './ChangePasswordLogin'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  components: {
    ChangePasswordLogin
  },
  data () {
    return {
      form: {
        username: '',
        password: '',
        remember: []
      },
      show_alert: false,
      user: {},
      show_password_modal: false
    }
  },
  methods: {
    setFirstLogin () {
      const path = basePath + '/user/first_login'
      axios.get(path)
        .then(response => {
          console.log(response.data)
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    getUser () {
      const path = basePath + '/user'
      axios.get(path)
        .then(response => {
          this.user = response.data
          if (this.user.first_login) {
            this.show_password_modal = true
            this.setFirstLogin()
          } else {
            this.$router.push({
              name: 'Index'
            })
          }
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    postLogin (evt) {
      evt.preventDefault()
      const path = basePath + '/auth/login'
      var payload = new URLSearchParams()

      payload.append('username', this.form.username)
      payload.append('password', this.form.password)
      payload.append('remember', this.form.remember)

      axios.post(path, payload)
        .then(response => {
          this.getUser()
        })
        .catch(error => {
          this.form.password = ''
          this.show_alert = true
          console.error(error.response.data)
        })
    },
    isAuth () {
      const path = basePath + '/user/is_auth'
      axios.get(path)
        .then(response => {
          this.$router.push({
            name: 'Index'
          })
        })
    }
  },
  created () {
    this.isAuth()
  }
}
</script>

<style>
</style>
