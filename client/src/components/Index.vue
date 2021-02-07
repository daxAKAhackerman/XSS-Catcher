<template>
  <b-container>
    <b-row>
      <b-col sm="9" class="text-left">
        <b-img height="75px" src="/logo.png" />
        <b-img height="40px" src="/title.png" />
      </b-col>
      <b-col sm="3" class="text-right">
        <p v-if="user.is_admin" style="margin-bottom: 0; margin-top: revert">
          Current user:
          <b>{{ user.username }}</b
          >&nbsp;
          <b-link v-b-modal.settings-modal>
            <b-icon-gear></b-icon-gear>
          </b-link>
        </p>
        <p v-else style="margin-bottom: 0; margin-top: revert">
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
            <b-button
              v-b-modal.add-client-modal
              type="button"
              variant="outline-success"
            >
              Add new client
            </b-button>
          </b-col>
          <b-col offset-sm="1" sm="8" class="text-right">
            <b-button
              variant="outline-secondary"
              v-b-tooltip.hover
              title="Refresh data"
              @click="
                getClients();
                makeToast('Data refreshed', 'success', 'OK');
              "
            >
              <b-icon-arrow-repeat
                style="width: 20px; height: 20px"
              ></b-icon-arrow-repeat>
            </b-button>
            <b-button
              v-if="user.is_admin"
              variant="outline-info"
              v-b-modal.manage-users-modal
              >Manage users</b-button
            >
            <b-button variant="outline-warning" v-b-modal.change-password-modal
              >Change password</b-button
            >
            <b-button type="button" variant="outline-warning" @click="getLogout"
              >Log out</b-button
            >
          </b-col>
        </b-row>
        <br />
        <b-row>
          <b-col offset-sm="8" sm="4">
            <b-input-group>
              <b-form-input
                size="sm"
                v-model="search"
                type="search"
                placeholder="Search"
              ></b-form-input>
              <b-input-group-append>
                <b-button
                  variant="outline-secondary"
                  size="sm"
                  :disabled="!search"
                  @click="search = ''"
                  >Clear</b-button
                >
              </b-input-group-append>
            </b-input-group>
          </b-col>
        </b-row>
        <br />
        <b-row>
          <b-table
            @filtered="onFiltered"
            :current-page="currentPage"
            :per-page="perPage"
            :items="clients"
            :fields="fields"
            :filter="search"
            hover
          >
            <template v-slot:cell(name)="row">
              <b-link
                @click="viewed_client = row.item"
                v-b-modal.view-client-modal
                >{{ row.item.name }}</b-link
              >
            </template>
            <template v-slot:cell(stored)="row">
              <b-link
                @click="
                  xss_type = 'stored';
                  viewed_client = row.item;
                "
                v-b-modal.view-XSS-modal
                >{{ row.item.stored }}</b-link
              >
            </template>
            <template v-slot:cell(reflected)="row">
              <b-link
                @click="
                  xss_type = 'reflected';
                  viewed_client = row.item;
                "
                v-b-modal.view-XSS-modal
                >{{ row.item.reflected }}</b-link
              >
            </template>
            <template v-slot:cell(data)="row">
              <b-link
                @click="viewed_client = row.item"
                v-b-modal.view-data-modal
                >{{ row.item.data }}</b-link
              >
            </template>
            <template v-slot:cell(action)="row">
              <b-button
                @click="viewed_client = row.item"
                v-b-modal.get-payload-modal
                type="button"
                variant="outline-info"
                >Generate payload</b-button
              >
              <b-button
                v-if="row.item.owner_id === user.id || user.is_admin"
                v-b-tooltip.hover
                title="Delete client"
                @click="to_delete = row.item.id"
                v-b-modal.delete-client-modal
                type="button"
                variant="outline-danger"
              >
                <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
              </b-button>
              <b-button v-else disabled type="button" variant="outline-danger">
                <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
              </b-button>
            </template>
          </b-table>
        </b-row>
        <b-row>
          <b-col sm="3">
            <b-pagination
              v-model="currentPage"
              :total-rows="totalRows"
              :per-page="perPage"
            ></b-pagination>
          </b-col>
          <b-col offset-sm="7" sm="2">
            <b-form-select
              size="sm"
              v-model="perPage"
              :options="[
                { value: 5, text: '-- Per page --' },
                { value: 5, text: '5' },
                { value: 10, text: '10' },
                { value: 25, text: '25' },
              ]"
              >-- Per page --</b-form-select
            >
          </b-col>
        </b-row>
      </b-col>
    </b-row>

    <b-modal
      ref="deleteClientModal"
      id="delete-client-modal"
      title="Are you sure?"
      hide-footer
    >
      <b-form>
        <div class="text-right">
          <b-button @click="deleteClient" variant="outline-danger"
            >Yes, delete this entry</b-button
          >
          <b-button
            @click="$refs.deleteClientModal.hide()"
            variant="outline-secondary"
            >Cancel</b-button
          >
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
    <Settings />
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
import Settings from "./Settings";

const basePath = "/api";

export default {
  components: {
    AddClient,
    GetPayload,
    ViewData,
    ViewXSS,
    ViewClient,
    ChangePassword,
    ManageUsers,
    Settings,
  },
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      fields: [
        {
          key: "name",
          sortable: true,
          label: "Client name",
        },
        {
          key: "stored",
          sortable: true,
          label: "Stored XSS",
        },
        {
          key: "reflected",
          sortable: true,
          label: "Reflected XSS",
        },
        {
          key: "data",
          sortable: true,
          label: "Data collected",
        },
        {
          key: "action",
          sortable: false,
          label: "Action",
        },
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
      search: "",
    };
  },
  methods: {
    getClients() {
      const path = basePath + "/client";
      axios
        .get(path)
        .then((response) => {
          this.clients = response.data;
          this.totalRows = this.clients.length;
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    deleteClient() {
      const path = basePath + "/client/" + this.to_delete;
      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.getClients();
          this.$refs.deleteClientModal.hide();
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    getLogout() {
      const path = basePath + "/auth/logout";
      axios
        .get(path)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.$router.push({ name: "Login" });
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    getUser() {
      const path = basePath + "/user/current";
      axios
        .get(path)
        .then((response) => {
          this.user = response.data;
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    makeToast(message, variant, title) {
      this.$root.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: variant,
      });
    },
    onFiltered(filteredItems) {
      this.totalRows = filteredItems.length;
    },
  },
  created() {
    this.getClients();
    this.getUser();
  },
};
</script>

<style>
</style>
