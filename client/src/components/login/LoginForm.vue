<template>
  <b-card>
    <b-form v-on:submit.prevent>
      <b-form-group
        id="input-group-username"
        label="Username:"
        label-for="input-field-username"
        v-if="!prompt_mfa"
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
        v-if="!prompt_mfa"
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
      <b-form-group
        id="input-group-otp"
        label="OTP:"
        label-for="input-field-otp"
        v-if="prompt_mfa"
      >
        <b-form-input
          @keyup.enter="postLogin()"
          id="input-field-otp"
          v-model="form.otp"
          autocomplete="off"
          placeholder="Enter one time password"
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
        otp: "",
      },
      prompt_mfa: false,
    };
  },
  methods: {
    postLogin() {
      const path = `${basePath}/auth/login`;
      const payload = {
        username: this.form.username,
        password: this.form.password,
        ...(this.form.otp ? { otp: this.form.otp } : undefined),
      };

      axiosLogin
        .post(path, payload)
        .then((response) => {
          if (response.data.msg && response.data.msg === "OTP is required") {
            this.prompt_mfa = true;
          } else {
            sessionStorage.setItem("access_token", response.data.access_token);
            sessionStorage.setItem(
              "refresh_token",
              response.data.refresh_token
            );
            this.makeToast("Logged in successfully", "success");
            this.$emit("login-process");
          }
        })
        .catch((error) => {
          if (error.response.data.msg === "Bad username or password") {
            this.form.password = "";
          }

          if (error.response.data.msg === "Bad OTP") {
            this.form.otp = "";
          }

          this.handleError(error);
        });
    },
  },
};
</script>

<style>
</style>
