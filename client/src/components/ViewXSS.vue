<template>

  <b-modal
    ref="viewXSSModal"
    id="view-XSS-modal"
    title="Triggered XSS"
    hide-footer
    size="xl"
    @show="getXSS"
    @hide="$parent.getClients"
  >

    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Timestamp</th>
          <th scope="col">Referer</th>
          <th scope="col">IP address</th>
          <th scope="col">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="hit in orderBy(dataXSS, 'timestamp')"
          v-bind:key="hit.id"
        >
          <td>{{ convertTimestamp(hit.timestamp) }} </td>
          <td>{{ hit.referer }}</td>
          <td>{{ hit.ip_addr}}</td>
          <td>
            <b-button
              type="button"
              variant="info"
              v-b-modal.view-details-modal
              @click="viewedXSS=hit"
            >View details
            </b-button>
            <b-button
              @click="deleteXSS(hit.id)"
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <ViewDetails :data=viewedXSS />

  </b-modal>

</template>

<script>

import axios from 'axios'
import Vue2Filters from 'vue2-filters'

import ViewDetails from './ViewDetails'
import moment from 'moment'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = 'http://127.0.0.1/api'

export default {
  components: {
    ViewDetails
  },
  props: ['xss_type', 'client_id'],
  mixins: [Vue2Filters.mixin],
  data () {
    return {
      dataXSS: {},
      viewedXSS: {}
    }
  },
  methods: {
    getXSS () {
      const path = basePath + '/client/' + this.client_id + '/' + this.xss_type

      axios.get(path)
        .then(response => {
          this.dataXSS = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    deleteXSS (xssID) {
      const path = basePath + '/xss/' + xssID

      axios.delete(path)
        .then(response => {
          this.getXSS()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    convertTimestamp (timestamp) {
      let timestampLocal = moment(timestamp).format('MM-DD-YYYY HH:mm:ss')
      return timestampLocal
    }
  }

}

</script>

<style></style>
