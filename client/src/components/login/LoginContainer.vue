<template>
  <b-container>
    <Logo />
    <br />
    <b-row align-v="center">
      <b-col md="4" offset-sm="4">
        <LoginForm
          @handle-error="handleError($event)"
          @login-process="loginProcess()"
        />
      </b-col>
    </b-row>
    <PasswordMfa
      :show_password_modal="show_password_modal"
      :mfa_set="user.mfa"
      :user_id="user.id"
    />
  </b-container>
</template>

<script>
import axios from "axios";

import PasswordMfa from "../shared/PasswordMfa";
import Logo from "./LogoRow";
import LoginForm from "./LoginForm";

const axiosLogin = axios.create();

const basePath = "/api";

export default {
  components: {
    PasswordMfa,
    Logo,
    LoginForm,
  },
  data() {
    return {
      user: {},
      show_password_modal: false,
    };
  },
  methods: {
    loginProcess() {
      const path = `${basePath}/user/current`;
      axiosLogin
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
          this.handleError(error);
        });
    },
    isAuth() {
      const path = `${basePath}/user/current`;
      axiosLogin
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
  },
  created() {
    axiosLogin.interceptors.request.use(
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
    this.isAuth();
  },
};
</script>

<style>
</style>
