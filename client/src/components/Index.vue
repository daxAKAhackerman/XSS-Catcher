<template>
  <b-container>
    <b-row>
      <b-col
        sm="9"
        class="text-left">
        <h1>XSS-Catcher</h1>
      </b-col>
      <b-col
        sm="2"
        class="text-right"
        >
        <p style="margin-bottom:0;margin-top:revert">Current user: <b>{{ user.username }}</b></p>
      </b-col>
    </b-row>
    <br />
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
            offset-sm="1"
            sm="8"
            class="text-right"
          >
            <b-button>
              <b-icon-arrow-repeat @click="getClients" style="width: 20px; height: 20px;"></b-icon-arrow-repeat>
            </b-button>
            <b-button variant="success" v-b-modal.create-user-modal>
              Create user
            </b-button>
            <b-button variant="danger" v-b-modal.manage-users-modal>
              Delete user
            </b-button>
            <b-button variant="warning" v-b-modal.change-password-modal>
              Change password
            </b-button>
            <b-button
              type="button"
              variant="warning"
              @click="getLogout"
            >Log out</b-button>
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
                  <b-link
                    @click="viewed_client=client.id"
                    v-b-modal.view-client-modal
                  >
                    {{ client.name }}
                  </b-link>
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
                    @click="to_delete = client.id"
                    v-b-modal.delete-client-modal
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

    <b-modal
    ref="deleteClientModal"
    id="delete-client-modal"
    title="Are you sure?"
    hide-footer
    >
      <b-form
        @submit="deleteClient"
        @reset="$refs.deleteClientModal.hide()"
      >
        <div class="text-right">
          <b-button
            type="submit"
            variant="danger"
          >Yes, delete this entry</b-button>
          <b-button type="reset">Cancel</b-button>
        </div>
      </b-form>
    </b-modal>

    <AddClient />
    <GetPayload :client_id=viewed_client />
    <ViewData :client_id=viewed_client />
    <ViewXSS
      :xss_type=xss_type
      :client_id=viewed_client
    />
    <ViewClient :client_id=viewed_client />
    <CreateUser />
    <ChangePassword />
    <ManageUsers />

  </b-container>
</template>

<script>
import axios from 'axios'
import Vue2Filters from 'vue2-filters'

import AddClient from './AddClient'
import GetPayload from './GetPayload'
import ViewData from './ViewData'
import ViewXSS from './ViewXSS'
import ViewClient from './ViewClient'
import CreateUser from './CreateUser'
import ChangePassword from './ChangePassword'
import ManageUsers from './ManageUsers'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  components: {
    AddClient,
    GetPayload,
    ViewData,
    ViewXSS,
    ViewClient,
    CreateUser,
    ChangePassword,
    ManageUsers
  },
  mixins: [Vue2Filters.mixin],
  data () {
    return {
      clients: {},
      viewed_client: '',
      xss_type: '',
      to_delete: 0,
      show_password_modal: false,
      user: {}
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
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    deleteClient () {
      const path = basePath + '/client/' + this.to_delete
      axios.delete(path)
        .then(response => {
          this.getClients()
          this.$refs.deleteClientModal.hide()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    getLogout () {
      const path = basePath + '/auth/logout'
      axios.get(path)
        .then(response => {
          this.$router.push({ name: 'Login' })
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    getUser () {
      const path = basePath + '/user'
      axios.get(path)
        .then(response => {
          this.user = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    }
  },
  created () {
    this.getClients()
    this.getUser()
  }
}
</script>

<style>
</style>
