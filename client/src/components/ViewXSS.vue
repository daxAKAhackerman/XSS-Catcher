<template>

  <b-modal
    ref="viewXSSModal"
    id="view-XSS-modal"
    title="Triggered XSS"
    hide-footer
    size="xl"
  >

  </b-modal>

</template>

<script>

import axios from 'axios'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = 'http://127.0.0.1/api'

export default {
  props: ['xss_type'],
  data () {
    return {
      data: {}
    }
  },
  methods: {

  }

}

</script>

<style></style>
