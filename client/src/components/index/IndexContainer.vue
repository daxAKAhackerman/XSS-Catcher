<template>
  <b-container>
    <HeaderRow :user="user" />
    <br />
    <b-row>
      <b-col offset-sm="1" sm="10">
        <Navigation
          @get-clients="getClients($event)"
          :user_is_admin="user.is_admin"
          @logout="logout()"
        />
        <br />
        <ClientTable
          :clients="clients"
          :totalRows="totalRows"
          :user="user"
          @view-client="viewed_client = $event"
          @view-stored="
            viewed_client = $event;
            xss_type = 'stored';
          "
          @view-reflected="
            viewed_client = $event;
            xss_type = 'reflected';
          "
          @view-data="viewed_client = $event"
          @generate-payload="viewed_client = $event"
          @delete-client="to_delete = $event"
          @set-total-rows="totalRows = $event"
        />
      </b-col>
    </b-row>

    <AddClient @get-clients="getClients(false)" />
    <GetPayload
      :client_id="viewed_client.id"
      @get-clients="getClients(false)"
    />
    <ViewData
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
      @get-clients="getClients(false)"
    />
    <ViewXSS
      :xss_type="xss_type"
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
      @get-clients="getClients(false)"
    />
    <ViewClient
      :client_id="viewed_client.id"
      :is_admin="user.is_admin"
      :owner_id="viewed_client.owner_id"
      :user_id="user.id"
      @get-clients="getClients(false)"
    />
    <ChangePassword :show_password_modal="show_password_modal" />
    <ManageUsers />
    <Settings />
    <DeleteClient :to_delete="to_delete" @get-clients="getClients(false)" />
  </b-container>
</template>

<script>
import axios from "axios";

import AddClient from "./addNewClient/AddClient";
import GetPayload from "./generatePayload/GetPayload";
import ViewData from "./viewData/ViewData";
import ViewXSS from "./viewXSS/ViewXSS";
import ViewClient from "./viewClient/ViewClient";
import ChangePassword from "../shared/ChangePassword";
import ManageUsers from "./manageUsers/ManageUsers";
import Settings from "./settings/SettingsModal";
import DeleteClient from "./DeleteClient";
import ClientTable from "./ClientTable";
import Navigation from "./NavigationRow";
import HeaderRow from "./HeaderRow";

const axiosRefresh = axios.create();

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
    DeleteClient,
    ClientTable,
    Navigation,
    HeaderRow,
  },
  data() {
    return {
      clients: [],
      viewed_client: "",
      xss_type: "",
      to_delete: 0,
      show_password_modal: false,
      user: {},
      totalRows: 0,
    };
  },
  methods: {
    getClients(is_refresh) {
      const path = `${basePath}/client`;
      axios
        .get(path)
        .then((response) => {
          this.clients = response.data;
          this.totalRows = this.clients.length;
          if (is_refresh) {
            this.makeToast("Data refreshed", "success", "OK");
          }
          this.getUser();
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    logout() {
      const path = `${basePath}/auth/logout`;
      axiosRefresh
        .post(path)
        .then((response) => {
          sessionStorage.removeItem("access_token");
          sessionStorage.removeItem("refresh_token");
          this.$router.push({ name: "Login" });
          this.makeToast(response.data.msg, "success");
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    getUser() {
      const path = `${basePath}/user/current`;
      axios
        .get(path)
        .then((response) => {
          this.user = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
  },
  created() {
    axios.interceptors.request.use(
      (config) => {
        const token = sessionStorage.getItem("access_token");

        if (token) {
          config.headers["Authorization"] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    axiosRefresh.interceptors.request.use(
      (config) => {
        const token = sessionStorage.getItem("refresh_token");

        if (token) {
          config.headers["Authorization"] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    axios.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        let originalRequest = error.config;

        if (error.response.status === 422) {
          sessionStorage.removeItem("access_token");
          sessionStorage.removeItem("refresh_token");
          delete originalRequest.headers.Authorization;
          return axios(originalRequest);
        }
        if (error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          return axiosRefresh
            .post(`${basePath}/auth/refresh`)
            .then((response) => {
              sessionStorage.setItem(
                "access_token",
                response.data.access_token
              );
              return axios(originalRequest);
            });
        }
        return Promise.reject(error);
      }
    );
    this.getClients(false);
  },
};
</script>

<style>
</style>
