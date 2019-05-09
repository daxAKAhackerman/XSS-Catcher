<template>
  <b-container>

    <b-row>
      <b-col
        offset-sm="1"
        sm="10"
      >
        <b-row>
          <b-col
            sm="3"
            class="text-left"
          >
            <b-button
              v-b-modal.add-client-modal
              type="button"
              variant="success"
            >Add
              new client</b-button>
          </b-col>
          <b-col
            offset-sm="3"
            sm="6"
          >
          </b-col>
        </b-row>
        <br />
        <b-row>

          <table class="table table-hover">
            <thead>
              <tr>
                <th scope="col">Client name</th>
                <th scope="col">Stored XSS</th>
                <th scope="col">Reflected XSS</th>
                <th scope="col">Data collected</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="client in orderBy(clients, 'name')"
                v-bind:key="client.id"
              >
                <td>
                  {{ client.name }}

                </td>
                <td>
                  <b-link
                    @click="xss_type='stored'; viewed_client=client.id"
                    v-b-modal.view-XSS-modal
                  >{{ client.stored }}</b-link>
                </td>
                <td>
                  <b-link
                    @click="xss_type='reflected'; viewed_client=client.id"
                    v-b-modal.view-XSS-modal
                  >{{ client.reflected }}
                  </b-link>
                </td>
                <td>
                  <b-link
                    @click="viewed_client=client.id"
                    v-b-modal.view-data-modal
                  >{{ client.cookies }}
                  </b-link>
                </td>
                <td>
                  <b-button
                    @click="viewed_client=client.id"
                    v-b-modal.get-payload-modal
                    type="button"
                    variant="info"
                  >Generate payload
                  </b-button>
                  <b-button
                    @click="deleteClient(client.id)"
                    type="button"
                    variant="danger"
                  >Delete
                  </b-button>
                </td>
              </tr>
            </tbody>
          </table>
        </b-row>
      </b-col>
    </b-row>

    <AddClient />
    <GetPayload :client_id=viewed_client />
    <ViewData :client_id=viewed_client />
    <ViewXSS
      :xss_type=xss_type
      :client_id=viewed_client
    />

  </b-container>
</template>

<script>
import axios from 'axios'
import Vue2Filters from 'vue2-filters'

import AddClient from './AddClient'
import GetPayload from './GetPayload'
import ViewData from './ViewData'
import ViewXSS from './ViewXSS'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = 'http://127.0.0.1/api'

export default {
  components: {
    AddClient,
    GetPayload,
    ViewData,
    ViewXSS
  },
  mixins: [Vue2Filters.mixin],
  data () {
    return {
      clients: {},
      viewed_client: '',
      xss_type: ''
    }
  },
  methods: {
    getClients () {
      const path = basePath + '/clients'
      axios.get(path)
        .then(response => {
          this.clients = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    deleteClient (clientId) {
      const path = basePath + '/client/' + clientId
      axios.delete(path)
        .then(response => {
          this.getClients()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    }
  },
  created () {
    this.getClients()
  }
}
</script>

<style>
</style>
