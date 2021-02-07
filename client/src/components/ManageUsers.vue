<template>
  <b-modal
    ref="manageUsersModal"
    id="manage-users-modal"
    title="Users"
    hide-footer
    size="md"
    @show="getUsers"
    @hide="cleanup"
  >
    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Username</th>
          <th scope="col" class="text-right">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in orderBy(users, 'username')" v-bind:key="user.id">
          <td v-if="user.is_admin">
            <b>{{ user.username }}</b> [admin]
          </td>
          <td v-else>
            <b>{{ user.username }}</b>
          </td>
          <td class="text-right">
            <b-button
              v-if="user.is_admin"
              v-b-tooltip.hover
              title="Demote user"
              @click="promoteUser(0, user.id)"
              type="button"
              variant="outline-danger"
            >
              <b-icon-chevron-double-down
                style="width: 20px; height: 20px"
              ></b-icon-chevron-double-down>
            </b-button>
            <b-button
              v-else
              v-b-tooltip.hover
              title="Promote user"
              @click="promoteUser(1, user.id)"
              type="button"
              variant="outline-success"
            >
              <b-icon-chevron-double-up
                style="width: 20px; height: 20px"
              ></b-icon-chevron-double-up>
            </b-button>
            <b-button
              v-b-tooltip.hover
              title="Reset password"
              @click="resetPassword(user.id, user.username)"
              type="button"
              variant="outline-warning"
            >
              <b-icon-arrow-repeat
                style="width: 20px; height: 20px"
              ></b-icon-arrow-repeat>
            </b-button>
            <b-button
              v-b-tooltip.hover
              title="Delete user"
              @click="to_delete = user.id"
              v-b-modal.delete-user-modal
              type="button"
              variant="outline-danger"
            >
              <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="text-right">
      <b-button variant="outline-success" v-b-modal.create-user-modal
        >Create user</b-button
      >
      <b-button variant="outline-secondary" type="reset" @click="cleanup"
        >Cancel</b-button
      >
    </div>
    <br v-if="show_alert" />
    <b-alert show :variant="alert_type" v-if="show_alert">{{
      alert_msg
    }}</b-alert>
    <b-modal
      ref="deleteUserModal"
      id="delete-user-modal"
      title="Are you sure?"
      hide-footer
    >
      <b-form>
        <div class="text-right">
          <b-button @click="deleteUser" variant="outline-danger"
            >Yes, delete this user</b-button
          >
          <b-button
            @click="$refs.deleteUserModal.hide()"
            variant="outline-secondary"
            >Cancel</b-button
          >
        </div>
      </b-form>
    </b-modal>

    <CreateUser />
  </b-modal>
</template>

<script>
import axios from "axios";
import Vue2Filters from "vue2-filters";

import CreateUser from "./CreateUser";

const basePath = "/api";

export default {
  components: {
    CreateUser,
  },
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      users: [],
      to_delete: 0,
      show_alert: false,
      alert_msg: "",
      alert_type: "danger",
    };
  },
  methods: {
    getUsers() {
      const path = basePath + "/user";

      axios
        .get(path)
        .then((response) => {
          this.users = response.data;
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
    deleteUser() {
      const path = basePath + "/user/" + this.to_delete;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.$refs.deleteUserModal.hide();
          this.getUsers();
          this.promote = 0;
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.$refs.deleteUserModal.hide();
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    promoteUser(promotion, userId) {
      const path = basePath + "/user/" + userId;

      const payload = {
        is_admin: promotion,
      };

      axios
        .patch(path, payload)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.getUsers();
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
    resetPassword(userId, username) {
      const path = basePath + "/user/" + userId + "/password";

      axios.post(path).then((response) => {
        this.alert_msg =
          "New password for user " + username + " is: " + response.data.detail;
        this.show_alert = true;
        this.alert_type = "success";
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
    cleanup() {
      this.users = [];
      this.to_delete = 0;
      this.show_alert = false;
      this.alert_msg = "";
      this.$refs.manageUsersModal.hide();
    },
  },
};
</script>

<style></style>
