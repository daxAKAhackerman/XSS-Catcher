<template>

  <b-modal
    ref="viewDataModal"
    id="view-data-modal"
    title="Captured data"
    hide-footer
    size="xl"
    @show="getData"
  >

    <h1 class="text-left">Cookies</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(cookie_value,cookie_id) in data.cookies"
          v-bind:key="cookie_id"
          class="text-left"
        >
          <td>{{ cookie_value }}</td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Local storage</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(local_storage_value,local_storage_id) in data.local_storage"
          v-bind:key="local_storage_id"
          class="text-left"
        >
          <td>{{ local_storage_value }}</td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Session storage</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(session_storage_value,session_storage_id) in data.session_storage"
          v-bind:key="session_storage_id"
          class="text-left"
        >
          <td>{{ session_storage_value }}</td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Other data</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(other_value,other_id) in data.other_data"
          v-bind:key="other_id"
          class="text-left"
        >
          <td>{{ other_value }}</td>
        </tr>
      </tbody>
    </table>

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
      data: {}
    }
  },
  methods: {
    getData () {
      const path = basePath + '/client/' + this.client_id + '/loot'

      axios.get(path)
        .then(response => {
          this.data = response.data
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
