<template>
  <b-modal
    ref="getPayloadModal"
    id="get-payload-modal"
    title="Payload"
    hide-footer
    @hidden="resetGetPayload"
  >
    <b-form @submit="getPayload">
      <b-form-group class="text-left">
        <p>{{ xss_payload }}</p>
        <b-form-checkbox
          v-model="options.stored"
          name="check-button"
          switch
        >
          Stored XSS
        </b-form-checkbox>
        <b-form-checkbox
          v-model="options.cookies"
          name="check-button"
          switch
        >
          Steal cookies
        </b-form-checkbox>
        <b-form-checkbox
          v-model="options.local_storage"
          name="check-button"
          switch
        >
          Steal local storage
        </b-form-checkbox>
        <b-form-checkbox
          v-model="options.session_storage"
          name="check-button"
          switch
        >
          Steal session storage
        </b-form-checkbox>
      </b-form-group>

      <b-button
        type="submit"
        variant="primary"
      >Generate</b-button>

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
      options: {
        cookies: false,
        local_storage: false,
        session_storage: false,
        stored: false
      },
      xss_payload: ''
    }
  },
  methods: {
    getPayload (evt) {
      evt.preventDefault()

      let path = basePath + '/xss/generate/' + this.client_id

      if (this.options.stored || this.options.cookies || this.options.local_storage || this.options.session_storage) {
        path += '?'
      }

      if (this.options.cookies) {
        path += 'cookie=1&'
      }

      if (this.options.local_storage) {
        path += 'local=1&'
      }

      if (this.options.session_storage) {
        path += 'session=1&'
      }

      if (this.options.stored) {
        path += 'stored=1'
      }

      if (path.substr(-1) === '&') {
        path = path.substr(0, path.length - 1)
      }

      axios.get(path)
        .then(response => {
          this.xss_payload = response.data
          this.$forceUpdate()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    resetGetPayload () {
      this.xss_payload = ''
      this.options = {}
      this.$refs.getPayloadModal.hide()
      this.$parent.getClients()
    }
  }

}

</script>

<style>
</style>
