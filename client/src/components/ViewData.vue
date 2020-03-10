<template>

  <b-modal
    ref="viewDataModal"
    id="view-data-modal"
    title="Captured data"
    hide-footer
    size="xl"
    @show="getData"
    @hide="$parent.getClients"
  >

    <h1 class="text-left">Cookies</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(cookie_value,cookie_id) in data.cookies"
          v-bind:key="cookie_id"
        >
          <td class="text-left">{{ cookie_value }}</td>
          <td class="text-right">
            <b-button
              @click="to_delete_type = 'cookies'; to_delete = cookie_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>

      </tbody>
    </table>

    <h1 class="text-left">Local storage</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(local_storage_value,local_storage_id) in data.local_storage"
          v-bind:key="local_storage_id"
        >
          <td class="text-left">{{ local_storage_value }}</td>
          <td class="text-right">
            <b-button
              @click="to_delete_type = 'local_storage'; to_delete = local_storage_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Session storage</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(session_storage_value,session_storage_id) in data.session_storage"
          v-bind:key="session_storage_id"
        >
          <td class="text-left">{{ session_storage_value }}</td>
          <td class="text-right">
            <b-button
              @click="to_delete_type = 'session_storage'; to_delete = session_storage_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Other data</h1>

    <table class="table table-hover">
      <tbody>
        <tr
          v-for="(other_value,other_id) in data.other_data"
          v-bind:key="other_id"
        >
          <td class="text-left">{{ other_value }}</td>
          <td class="text-right">
            <b-button
              @click="to_delete_type = 'other_data'; to_delete = other_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <b-modal
    ref="deleteDataModal"
    id="delete-data-modal"
    title="Are you sure?"
    hide-footer
    >
      <b-form
        @submit="deleteData"
        @reset="$refs.deleteDataModal.hide()"
      >

        <b-button
          type="submit"
          variant="danger"
        >Yes, delete this entry</b-button>
        <b-button type="reset">Cancel</b-button>

      </b-form>
    </b-modal>

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
      data: {},
      to_delete: 0,
      to_delete_type: ''
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
    },
    deleteData () {
      const path = basePath + '/xss/' + this.to_delete + '/' + this.to_delete_type

      axios.delete(path)
        .then(response => {
          this.getData()
          this.$refs.deleteDataModal.hide()
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
