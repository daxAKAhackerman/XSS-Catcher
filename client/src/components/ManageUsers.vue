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
          <th scope="col" class='text-right'>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="user in orderBy(users, 'username')"
          v-bind:key="user.id"
        >
          <td v-if="user.is_admin"><b>{{ user.username }}</b> [admin]</td>
          <td v-else><b>{{ user.username }}</b></td>
          <td class='text-right'>
            <b-button
              v-if="user.is_admin"
              v-b-tooltip.hover title="Demote user"
              @click="promoteUser(0, user.id)"
              type="button"
              variant="danger"
            ><b-icon-chevron-double-down style="width: 20px; height: 20px;"></b-icon-chevron-double-down>
            </b-button>
            <b-button
              v-else
              v-b-tooltip.hover title="Promote user"
              @click="promoteUser(1, user.id)"
              type="button"
              variant="success"
            ><b-icon-chevron-double-up style="width: 20px; height: 20px;"></b-icon-chevron-double-up>
            </b-button>
            <b-button
              v-b-tooltip.hover title="Reset password"
              @click="resetPassword(user.id, user.username)"
              type="button"
              variant="warning"
            ><b-icon-arrow-repeat style="width: 20px; height: 20px;"></b-icon-arrow-repeat>
            </b-button>
            <b-button
              v-b-tooltip.hover title="Delete user"
              @click="to_delete = user.id"
              v-b-modal.delete-user-modal
              type="button"
              variant="danger"
            ><b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="text-right">
      <b-button variant="success" v-b-modal.create-user-modal>
        Create user
      </b-button>
      <b-button type="reset" @click="cleanup">Cancel</b-button>
    </div>
    <br v-if="show_alert" />
    <b-alert
      show
      :variant="alert_type"
      v-if="show_alert"
    >{{ alert_msg }}</b-alert>
    <b-modal
    ref="deleteUserModal"
    id="delete-user-modal"
    title="Are you sure?"
    hide-footer
    >
      <b-form
        @submit="deleteUser"
        @reset="$refs.deleteUserModal.hide()"
      >
        <div class="text-right">
          <b-button
            type="submit"
            variant="danger"
          >Yes, delete this user</b-button>
          <b-button type="reset">Cancel</b-button>
        </div>
      </b-form>
    </b-modal>

    <CreateUser />

  </b-modal>

</template>

<script>

import axios from 'axios'
import Vue2Filters from 'vue2-filters'

import CreateUser from './CreateUser'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  components: {
    CreateUser
  },
  mixins: [Vue2Filters.mixin],
  data () {
    return {
      users: [],
      to_delete: 0,
      show_alert: false,
      alert_msg: '',
      alert_type: 'danger'
    }
  },
  methods: {
    getUsers () {
      const path = basePath + '/user/all'

      axios.get(path)
        .then(response => {
          this.users = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    deleteUser () {
      const path = basePath + '/user/' + this.to_delete

      axios.delete(path)
        .then(response => {
          this.$refs.deleteUserModal.hide()
          this.getUsers()
          this.promote = 0
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            this.$refs.deleteUserModal.hide()
            this.alert_msg = error.response.data.detail
            this.show_alert = true
            this.alert_type = 'danger'
          }
        })
    },
    promoteUser (promotion, userId) {
      const path = basePath + '/user/' + userId

      var payload = new URLSearchParams()

      payload.append('is_admin', promotion)

      axios.post(path, payload)
        .then(response => {
          this.getUsers()
          this.alert_msg = ''
          this.alert_type = 'success'
          this.show_alert = false
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            this.show_alert = true
            this.alert_msg = error.response.data.detail
            this.alert_type = 'danger'
          }
        })
    },
    resetPassword (userId, username) {
      const path = basePath + '/user/' + userId + '/reset_password'

      axios.post(path)
        .then(response => {
          this.alert_msg = 'New password for user ' + username + ' is: ' + response.data.detail
          this.show_alert = true
          this.alert_type = 'success'
        })
    },
    cleanup () {
      this.users = []
      this.to_delete = 0
      this.show_alert = false
      this.alert_msg = ''
      this.$refs.manageUsersModal.hide()
    }
  }

}

</script>

<style></style>
