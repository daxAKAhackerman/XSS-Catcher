<template>
  <b-container>
    <b-row>
      <b-col>
        <b-img height="200px" src="/logo.png" />
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <b-img height="50px" src="/title.png" />
      </b-col>
    </b-row>
    <br />
    <b-row align-v="center">
      <b-col md="4" offset-sm="4">
        <b-card>
          <b-form>
            <b-form-group
              id="input-group-username"
              label="Username:"
              label-for="input-field-username"
            >
              <b-form-input
                @keyup.enter="postLogin"
                id="input-field-username"
                v-model="form.username"
                required
                placeholder="Enter username"
              ></b-form-input>
            </b-form-group>
            <b-form-group
              id="input-group-password"
              label="Password:"
              label-for="input-field-password"
            >
              <b-form-input
                @keyup.enter="postLogin"
                type="password"
                id="input-field-password"
                v-model="form.password"
                required
                placeholder="Enter password"
              ></b-form-input>
            </b-form-group>
            <b-button @click="postLogin" variant="outline-info">Login</b-button>
          </b-form>
        </b-card>
      </b-col>
    </b-row>
    <ChangePassword />
  </b-container>
</template>

<script>
import axios from "axios";

import ChangePassword from "./ChangePassword";

const basePath = "/api";

export default {
  components: {
    ChangePassword,
  },
  data() {
    return {
      form: {
        username: "",
        password: "",
      },
      user: {},
      show_password_modal: false,
    };
  },
  methods: {
    handleAuthError(error) {
      if (error.response.status === 401) {
        this.$router.push({ name: "Login" });
      } else if (error.response.status === 422) {
        sessionStorage.removeItem("access_token");
        delete axios.defaults.headers.common["Authorization"];
        this.$router.push({ name: "Login" });
      }
    },
    loginProcess() {
      const path = basePath + "/user/current";
      axios
        .get(path)
        .then((response) => {
          this.user = response.data;
          if (this.user.first_login) {
            this.show_password_modal = true;
          } else {
            this.$router.push({
              name: "Index",
            });
          }
        })
        .catch((error) => {
          this.handleAuthError(error);
        });
    },
    postLogin() {
      const path = basePath + "/auth/login";
      const payload = {
        username: this.form.username,
        password: this.form.password,
      };

      axios
        .post(path, payload)
        .then((response) => {
          sessionStorage.setItem(
            "access_token",
            response.data.detail.access_token
          );
          if (sessionStorage.getItem("access_token") !== null) {
            axios.defaults.headers.common["Authorization"] =
              "Bearer " + sessionStorage.getItem("access_token");
          }
          this.makeToast(
            "Logged in successfully",
            "success",
            response.data.status
          );
          this.loginProcess();
        })
        .catch((error) => {
          this.form.password = "";
          this.makeToast(
            error.response.data.detail,
            "danger",
            error.response.data.status
          );
        });
    },
    isAuth() {
      if (sessionStorage.getItem("access_token") !== null) {
        axios.defaults.headers.common["Authorization"] =
          "Bearer " + sessionStorage.getItem("access_token");
      }
      const path = basePath + "/user/current";
      axios
        .get(path)
        .then((response) => {
          void response;
          this.$router.push({
            name: "Index",
          });
        })
        .catch((error) => {
          void error;
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
  },
  created() {
    this.isAuth();
  },
};
</script>

<style>
</style>
