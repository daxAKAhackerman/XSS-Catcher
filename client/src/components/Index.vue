<template>
  <b-container>
    <b-row>
      <b-col sm="9" class="text-left">
        <h1>XSS-Catcher</h1>
      </b-col>
      <b-col sm="3" class="text-right">
        <p v-if="user.is_admin" style="margin-bottom:0;margin-top:revert">
          Current user:
          <b>{{ user.username }}</b> [admin]
        </p>
        <p v-else style="margin-bottom:0;margin-top:revert">
          Current user:
          <b>{{ user.username }}</b>
        </p>
      </b-col>
    </b-row>
    <br />
    <b-row>
      <b-col offset-sm="1" sm="10">
        <b-row>
          <b-col sm="3" class="text-left">
            <b-button v-b-modal.add-client-modal type="button" variant="success">
              Add
              new client
            </b-button>
          </b-col>
          <b-col offset-sm="1" sm="8" class="text-right">
            <b-button v-b-tooltip.hover title="Refresh data" @click="getClients">
              <b-icon-arrow-repeat style="width: 20px; height: 20px;"></b-icon-arrow-repeat>
            </b-button>
            <b-button v-if="user.is_admin" variant="info" v-b-modal.manage-users-modal>Manage users</b-button>
            <b-button variant="warning" v-b-modal.change-password-modal>Change password</b-button>
            <b-button type="button" variant="warning" @click="getLogout">Log out</b-button>
          </b-col>
        </b-row>
        <br />
        <b-row>
          <b-col offset-sm="8" sm="4">
            <b-input-group>
              <b-form-input size="sm" v-model="search" type="search" placeholder="Search"></b-form-input>
              <b-input-group-append>
                <b-button size="sm" :disabled="!search" @click="search = ''">Clear</b-button>
              </b-input-group-append>
            </b-input-group>
          </b-col>
        </b-row>
        <br />
        <b-row>
          <b-table
            :current-page="currentPage"
            :per-page="perPage"
            :items="clients"
            :fields="fields"
            :filter="search"
            hover
          >
            <template v-slot:cell(name)="row">
              <b-link
                @click="viewed_client=row.item"
                v-b-modal.view-client-modal
              >{{ row.item.name }}</b-link>
            </template>
            <template v-slot:cell(stored)="row">
              <b-link
                @click="xss_type='stored'; viewed_client=row.item"
                v-b-modal.view-XSS-modal
              >{{ row.item.stored }}</b-link>
            </template>
            <template v-slot:cell(reflected)="row">
              <b-link
                @click="xss_type='reflected'; viewed_client=row.item"
                v-b-modal.view-XSS-modal
              >{{ row.item.reflected }}</b-link>
            </template>
            <template v-slot:cell(data)="row">
              <b-link @click="viewed_client=row.item" v-b-modal.view-data-modal>{{ row.item.data }}</b-link>
            </template>
            <template v-slot:cell(action)="row">
              <b-button
                @click="viewed_client=row.item"
                v-b-modal.get-payload-modal
                type="button"
                variant="info"
              >Generate payload</b-button>
              <b-button
                v-if="row.item.owner_id === user.id || user.is_admin"
                v-b-tooltip.hover
                title="Delete client"
                @click="to_delete = row.item.id"
                v-b-modal.delete-client-modal
                type="button"
                variant="danger"
              >
                <b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
              </b-button>
              <b-button v-else disabled type="button" variant="danger">Delete</b-button>
            </template>
          </b-table>
        </b-row>
        <b-row>
          <b-col sm="3">
            <b-pagination v-model="currentPage" :total-rows="totalRows" :per-page="perPage"></b-pagination>
          </b-col>
          <b-col offset-sm="7" sm="2">
            <b-form-select
              size="sm"
              v-model="perPage"
              :options="[{ value: 5, text: '-- Per page --' },{ value: 5, text: '5' },{ value: 10, text: '10' },{ value: 25, text: '25' }]"
            >-- Per page --</b-form-select>
          </b-col>
        </b-row>
      </b-col>
    </b-row>

    <b-modal ref="deleteClientModal" id="delete-client-modal" title="Are you sure?" hide-footer>
      <b-form @submit="deleteClient" @reset="$refs.deleteClientModal.hide()">
        <div class="text-right">
          <b-button type="submit" variant="danger">Yes, delete this entry</b-button>
          <b-button type="reset">Cancel</b-button>
        </div>
      </b-form>
    </b-modal>

    <AddClient />
    <GetPayload :client_id="viewed_client.id" />
    <ViewData
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
    />
    <ViewXSS
      :xss_type="xss_type"
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
    />
    <ViewClient
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
    />
    <ChangePassword />
    <ManageUsers />
  </b-container>
</template>

<script>
import axios from "axios";
import Vue2Filters from "vue2-filters";

import AddClient from "./AddClient";
import GetPayload from "./GetPayload";
import ViewData from "./ViewData";
import ViewXSS from "./ViewXSS";
import ViewClient from "./ViewClient";
import ChangePassword from "./ChangePassword";
import ManageUsers from "./ManageUsers";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  components: {
    AddClient,
    GetPayload,
    ViewData,
    ViewXSS,
    ViewClient,
    ChangePassword,
    ManageUsers
  },
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      fields: [
        {
          key: "name",
          sortable: true,
          label: "Client name"
        },
        {
          key: "stored",
          sortable: true,
          label: "Stored XSS"
        },
        {
          key: "reflected",
          sortable: true,
          label: "Reflected XSS"
        },
        {
          key: "data",
          sortable: true,
          label: "Data collected"
        },
        {
          key: "action",
          sortable: false,
          label: "Action"
        }
      ],
      clients: [],
      viewed_client: "",
      xss_type: "",
      to_delete: 0,
      show_password_modal: false,
      user: {},
      perPage: 5,
      currentPage: 1,
      totalRows: 0,
      search: ""
    };
  },
  methods: {
    getClients() {
      const path = basePath + "/clients";
      axios
        .get(path)
        .then(response => {
          this.clients = response.data;
          this.totalRows = this.clients.length;
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    deleteClient() {
      const path = basePath + "/client/" + this.to_delete;
      axios
        .delete(path)
        .then(response => {
          void response;
          this.getClients();
          this.$refs.deleteClientModal.hide();
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    getLogout() {
      const path = basePath + "/auth/logout";
      axios
        .get(path)
        .then(response => {
          void response;
          this.$router.push({ name: "Login" });
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    getUser() {
      const path = basePath + "/user";
      axios
        .get(path)
        .then(response => {
          this.user = response.data;
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    }
  },
  created() {
    this.getClients();
    this.getUser();
  }
};
</script>

<style>
</style>
