<template>

  <b-modal
    ref="viewClientModal"
    id="view-client-modal"
    title="Client"
    hide-footer
    @show="getClient"
    @hide="resetClient"
  >
    <b-form
      @submit="postClient"
      @reset="resetClient"
    >

      <b-form-group
        id="input-group-name"
        label="Short name:"
        label-cols="3"
        label-for="input-field-name"
      >
        <b-form-input
          id="input-field-name"
          v-model="client.name"
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-full_name"
        label="Full name:"
        label-cols="3"
        label-for="input-field-full_name"
      >
        <b-form-input
          id="input-field-full_name"
          v-model="client.full_name"
        ></b-form-input>
      </b-form-group>

      <b-button
        type="submit"
        variant="info"
      >Save</b-button>
      <b-button
        type="reset"
        variant="secondary"
      >Cancel</b-button>
    </b-form>

  </b-modal>

</template>

<script>

import axios from 'axios'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = 'http://127.0.0.1/api'

export default {
  props: ['client_id'],
  data () {
    return {
      client: {}
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
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    postClient () {
      const path = basePath + '/client/' + this.client_id

      var payload = new URLSearchParams()

      payload.append('name', this.client.name)
      payload.append('full_name', this.client.full_name)

      axios.post(path, payload)
        .then(response => {
          this.resetClient()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    resetClient () {
      this.client = {}
      this.$refs.viewClientModal.hide()
      this.$parent.getClients()
    }
  }

}

</script>

<style></style>
