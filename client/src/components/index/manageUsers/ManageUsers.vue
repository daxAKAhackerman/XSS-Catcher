<template>
  <b-modal ref="manageUsersModal" id="manage-users-modal" title="Users" hide-footer size="lg" @show="getUsers()"
    @hide="cleanup()">
    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Username</th>
          <th scope="col" class="text-right"></th>
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
            <b-button v-if="user.is_admin" v-b-tooltip.hover title="Demote user" @click="promoteUser(false, user.id)"
              type="button" variant="outline-danger">
              <b-icon-chevron-double-down style="width: 20px; height: 20px"></b-icon-chevron-double-down>
            </b-button>
            <b-button v-else v-b-tooltip.hover title="Promote user" @click="promoteUser(true, user.id)" type="button"
              variant="outline-success">
              <b-icon-chevron-double-up style="width: 20px; height: 20px"></b-icon-chevron-double-up>
            </b-button>
            <b-button class="ml-2" v-if="user.mfa" v-b-tooltip.hover title="Disable MFA" @click="disableMfa(user.id)" type="button"
              variant="outline-danger">
              <b-icon-lock style="width: 20px; height: 20px"></b-icon-lock>
            </b-button>
            <b-button class="ml-2" v-else v-b-tooltip.hover title="MFA not enabled" type="button" variant="outline-danger" disabled>
              <b-icon-unlock style="width: 20px; height: 20px"></b-icon-unlock>
            </b-button>
            <b-button class="ml-2" v-b-tooltip.hover title="Reset password" @click="resetPassword(user.id, user.username)"
              type="button" variant="outline-success">
              <b-icon-arrow-repeat style="width: 20px; height: 20px"></b-icon-arrow-repeat>
            </b-button>
            <b-button class="ml-2" v-b-tooltip.hover title="API keys" @click="apiKeysOwner = user" v-b-modal.manage-api-keys-modal
              type="button" variant="outline-success">
              <b-icon-key style="width: 20px; height: 20px"></b-icon-key>
            </b-button>
            <b-button class="ml-2" v-b-tooltip.hover title="Delete user" @click="to_delete = user.id" v-b-modal.delete-user-modal
              type="button" variant="outline-danger">
              <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="text-right">
      <b-button variant="outline-success" v-b-modal.create-user-modal>Create user</b-button>
      <b-button class="ml-2" variant="outline-secondary" type="reset" @click="cleanup()">Cancel</b-button>
    </div>
    <br v-if="show_alert" />
    <b-alert show :variant="alert_type" v-if="show_alert">{{
    alert_msg
}}</b-alert>

    <DeleteUser :to_delete="to_delete" @get-users="getUsers" @cleanup="to_delete = undefined"/>
    <CreateUser @get-users="getUsers" />
    <ManageApiKeys :user="apiKeysOwner" @cleanup="apiKeysOwner = {}" />
  </b-modal>
</template>

<script>
import axios from "axios"
import Vue2Filters from "vue2-filters"

import CreateUser from "./CreateUser"
import DeleteUser from "./DeleteUser"
import ManageApiKeys from "./ManageApiKeys"

const basePath = "/api"

export default {
  components: {
    CreateUser,
    DeleteUser,
    ManageApiKeys,
  },
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      users: [],
      to_delete: undefined,
      show_alert: false,
      alert_msg: "",
      alert_type: "danger",
      apiKeysOwner: {}
    }
  },
  methods: {
    getUsers() {
      const path = `${basePath}/user`

      axios
        .get(path)
        .then((response) => {
          this.users = response.data
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    promoteUser(promotion, userId) {
      const path = `${basePath}/user/${userId}`

      const payload = {
        is_admin: promotion,
      }

      axios
        .patch(path, payload)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.getUsers()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    resetPassword(userId, username) {
      const path = `${basePath}/user/${userId}/password`

      axios
        .post(path)
        .then((response) => {
          this.alert_msg = `New password for user ${username} is: ${response.data.password}`
          this.show_alert = true
          this.alert_type = "success"
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    disableMfa(userId) {
      const path = `${basePath}/user/${userId}/mfa`

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.msg, "success")
          this.cleanup()
        })
        .catch((error) => {
          this.handleError(error)
        })
    },
    cleanup() {
      this.users = []
      this.to_delete = undefined
      this.apiKeysOwner = {}
      this.show_alert = false
      this.alert_msg = ""
      this.$refs.manageUsersModal.hide()
    },
  },
}
</script>

<style>

</style>
