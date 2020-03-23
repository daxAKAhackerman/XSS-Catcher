<template>

  <b-modal
    ref="viewClientModal"
    id="view-client-modal"
    title="Client"
    hide-footer
    @show="getClient"
    @hide="cleanup"
  >
    <b-form
      @submit="postClient"
      @reset="cleanup"
    >

      <b-form-group
        id="input-group-name"
        label="Short name:"
        label-cols="3"
        label-for="input-field-name"
      >
        <b-form-input
          v-if="owner_id === user_id || is_admin"
          id="input-field-name"
          v-model="client.name"
        ></b-form-input>
        <b-form-input
          v-else
          disabled
          id="input-field-name"
          v-model="client.name"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-description"
        label="Description:"
        label-cols="3"
        label-for="input-field-description"
      >
        <b-form-input
          v-if="owner_id === user_id || is_admin"
          id="input-field-description"
          v-model="client.description"
        ></b-form-input>
        <b-form-input
          v-else
          disabled
          id="input-field-description"
          v-model="client.description"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-owner"
        label="Owner:"
        label-cols="3"
        label-for="input-field-owner"
      >
        <b-form-input
          id="input-field-owner"
          v-model="client.owner"
          disabled
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button
          v-if="owner_id === user_id || is_admin" 
          type="submit"
          variant="info"
        >Save</b-button>
        <b-button
          type="reset"
          variant="secondary"
        >Cancel</b-button>
      </div>
    </b-form>
    <br v-if="show_alert" />
    <b-alert
      show
      variant="danger"
      v-if="show_alert"
    >{{ alert_msg }}</b-alert>
  </b-modal>

</template>

<script>

import axios from 'axios'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  props: ['client_id', 'is_admin', 'owner_id', 'user_id'],
  data () {
    return {
      client: {},
      show_alert: false,
      alert_msg: ''
    }
  },
  methods: {
    getClient () {
      const path = basePath + '/client/' + this.client_id

      axios.get(path)
        .then(response => {
          this.client = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    postClient () {
      const path = basePath + '/client/' + this.client_id

      var payload = new URLSearchParams()

      payload.append('name', this.client.name)
      payload.append('description', this.client.description)

      axios.post(path, payload)
        .then(response => {
          this.cleanup()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            this.alert_msg = error.response.data.detail
            this.show_alert = true
          }
        })
    },
    cleanup () {
      this.show_alert = false
      this.alert_msg = ''
      this.client = {}
      this.$refs.viewClientModal.hide()
      this.$parent.getClients()
    }
  }

}

</script>

<style></style>
