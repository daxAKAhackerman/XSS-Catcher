<template>

  <b-modal
    ref="viewDetailsModal"
    id="view-details-modal"
    title="Details"
    hide-footer
    size="xl"
  >

    <table class="table" style="table-layout: fixed; width: 100%">
      <tr>
        <td valign="top"><b>Timestamp: </b></td>
        <td width="80%">{{ converted_timestamp }}</td>
      </tr>
      <tr>
        <td valign="top"><b>Referer: </b></td>
        <td>{{ data.referer }}</td>
      </tr>
      <tr>
        <td valign="top"><b>IP address: </b></td>
        <td>{{ data.ip_addr }}</td>
      </tr>
      <tr>
        <td valign="top"><b>User agent: </b></td>
        <td>{{ data.user_agent }}</td>
      </tr>
      <tr>
        <td valign="top"><b>Captured cookies: </b></td>
        <td><code>{{ data.cookies }}</code></td>
      </tr>
      <tr>
        <td valign="top"><b>Captured local storage: </b></td>
        <td><code>{{ data.local_storage }}</code></td>
      </tr>
      <tr>
        <td valign="top"><b>Captured session storage: </b></td>
        <td><code>{{ data.session_storage }}</code></td>
      </tr>
      <tr>
        <td valign="top"><b>Other captured data: </b></td>
        <td>
          <div v-for="(value, key) in data.other_data" v-bind:key="key" style="word-wrap: break-word">
            <div v-if="key == 'fingerprint'">
              <h4>Fingerprint</h4>
              <p><vue-json-pretty :showLength=true :deep=0 :data=value></vue-json-pretty></p>
            </div>
            <div v-else-if="key == 'screenshot'">
              <h4>Screenshot</h4>
              <p><img style="max-width:100%" :src=value /></p>
            </div>
            <div v-else>
              <h4>Data</h4>
              <p><code>{{ key }} => {{ value}}</code></p>
            </div>
          </div>
        </td>
      </tr>
    </table>

  </b-modal>

</template>

<script>
import moment from 'moment'
import VueJsonPretty from 'vue-json-pretty'

export default {
  props: ['data'],
  components: {
    VueJsonPretty
  },
  computed: {
    converted_timestamp: {
      get () {
        return this.convertTimestamp(this.data.timestamp)
      }
    }
  },
  methods: {
    convertTimestamp (timestamp) {
      let timestampLocal = moment(timestamp).format('dddd MMMM Do YYYY, h:mm:ss a')
      return timestampLocal
    }
  }
}

</script>

<style></style>
