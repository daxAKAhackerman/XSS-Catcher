<template>
  <b-modal
    size="md"
    ref="getPayloadModal"
    id="get-payload-modal"
    title="Payload"
    hide-footer
    @hidden="cleanup"
  >
    <b-form @submit="getPayload" @reset="cleanup">
      <b-form-group class="text-left">
        <p style="overflow-wrap:break-word" v-if="xss_payload !== ''"><kbd>{{ xss_payload }}</kbd></p>
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
        <b-form-checkbox
          v-model="options.geturl"
          name="check-button"
          switch
        >
          Get origin URL
        </b-form-checkbox>

        <b-form-radio v-model="options.code_type" name="radio-button" value="js">JavaScript</b-form-radio>
        <b-form-radio v-model="options.code_type" name="radio-button" value="html">HTML</b-form-radio>
      </b-form-group>
      <b-form-group
      label="Other data: ">
        <b-form-input
          v-model="options.other"
          name="input"
          label="Other data: "
          placeholder="param1=value1&param2=value2"
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button
          type="submit"
          variant="info"
        >Generate</b-button>
        <b-button type="reset">Cancel</b-button>
      </div>
    </b-form>
  </b-modal>
</template>

<script>
import axios from 'axios'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  props: ['client_id'],
  data () {
    return {
      options: {
        cookies: false,
        local_storage: false,
        session_storage: false,
        stored: false,
        geturl: false,
        code_type: 'html',
        other: ''
      },
      xss_payload: ''
    }
  },
  methods: {
    getPayload (evt) {
      evt.preventDefault()

      let path = basePath + '/xss/generate/' + this.client_id + '?url=' + encodeURIComponent(location.origin) + '&'

      if (this.options.cookies) {
        path += 'cookies=1&'
      }

      if (this.options.local_storage) {
        path += 'local_storage=1&'
      }

      if (this.options.session_storage) {
        path += 'session_storage=1&'
      }

      if (this.options.stored) {
        path += 'stored=1&'
      }

      if (this.options.geturl) {
        path += 'geturl=1&'
      }

      if (this.options.other) {
        path += this.options.other + '&'
      }

      path += 'code=' + this.options.code_type

      if (path.substr(-1) === '&') {
        path = path.substr(0, path.length - 1)
      }

      axios.get(path)
        .then(response => {
          this.xss_payload = response.data
          this.$forceUpdate()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    cleanup () {
      this.xss_payload = ''
      this.options = {
        cookies: false,
        local_storage: false,
        session_storage: false,
        stored: false,
        code_type: 'html',
        other: ''
      }
      this.$refs.getPayloadModal.hide()
      this.$parent.getClients()
    }
  }

}

</script>

<style>
</style>
