<template>
  <b-card>
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-username"
        label="Username:"
        label-for="input-field-username"
      >
        <b-form-input
          @keyup.enter="postLogin()"
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
          @keyup.enter="postLogin()"
          type="password"
          id="input-field-password"
          v-model="form.password"
          required
          placeholder="Enter password"
        ></b-form-input>
      </b-form-group>
      <b-button @click="postLogin()" variant="outline-info">Login</b-button>
    </b-form>
  </b-card>
</template>
<script>
import axios from "axios";

const axiosLogin = axios.create();

const basePath = "/api";

export default {
  data() {
    return {
      form: {
        username: "",
        password: "",
      },
    };
  },
  methods: {
    postLogin() {
      const path = `${basePath}/auth/login`;
      const payload = {
        username: this.form.username,
        password: this.form.password,
      };

      axiosLogin
        .post(path, payload)
        .then((response) => {
          sessionStorage.setItem(
            "access_token",
            response.data.detail.access_token
          );
          sessionStorage.setItem(
            "refresh_token",
            response.data.detail.refresh_token
          );
          this.makeToast(
            "Logged in successfully",
            "success",
            response.data.status
          );
          this.$emit("login-process");
        })
        .catch((error) => {
          this.form.password = "";
          this.$emit("handle-error", error);
        });
    },
  },
};
</script>

<style>
</style>
