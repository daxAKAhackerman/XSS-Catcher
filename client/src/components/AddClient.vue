<template>
  <b-modal
    ref="addClientModal"
    id="add-client-modal"
    title="New client"
    hide-footer
    @hidden="resetNewClient"
  >
    <b-form
      @submit="putClient"
      @reset="resetNewClient"
    >
      <b-form-group
        id="input-group-name"
        label="Name:"
        label-cols="3"
        label-for="input-field-name"
      >
        <b-form-input
          v-model="client.name"
          id="input-field-name"
          required
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-full_name"
        label="Full name:"
        label-cols="3"
        label-for="input-field-full_name"
      >
        <b-form-input
          v-model="client.full_name"
          id="input-field-full_name"
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

const basePath = 'http://127.0.0.1/api'

export default {
  data () {
    return {
      client: {}
    }
  },
  methods: {
    putClient () {
      const path = basePath + '/client'

      var payload = new URLSearchParams()

      payload.append('name', this.client.name)
      payload.append('full_name', this.client.full_name)

      axios.put(path, payload)
        .then(response => {
          console.log(response.data)
          this.resetNewClient()
        })
        .catch(error => {
          console.error(error.response.data)
        })
    },
    resetNewClient () {
      this.client = {}
      this.$refs.addClientModal.hide()
      this.$parent.getClients()
    }
  }
}
</script>

<style>
</style>
