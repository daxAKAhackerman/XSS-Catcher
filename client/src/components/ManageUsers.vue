<template>

  <b-modal
    ref="manageUsersModal"
    id="manage-users-modal"
    title="Users"
    hide-footer
    size="md"
    @show="getUsers"
  >

    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Username</th>
          <th scope="col" class='text-center'>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="user in orderBy(users, 'username')"
          v-bind:key="user.id"
        >
          <td>{{ user.username }}</td>
          <td class='text-center'>
            <b-button
              @click="to_delete = user.id"
              v-b-modal.delete-user-modal
              type="button"
              variant="danger"
            >Delete
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

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

        <b-button
          type="submit"
          variant="danger"
        >Yes, delete this user</b-button>
        <b-button type="reset">Cancel</b-button>

      </b-form>
    </b-modal>

  </b-modal>

</template>

<script>

import axios from 'axios'
import Vue2Filters from 'vue2-filters'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  mixins: [Vue2Filters.mixin],
  data () {
    return {
      users: [],
      to_delete: 0
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
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    },
    deleteUser () {
      const path = basePath + '/user/' + this.to_delete

      axios.delete(path)
        .then(response => {
          this.$refs.deleteUserModal.hide()
          this.getUsers()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {
            console.error(error.response.data)
          }
        })
    }
  }

}

</script>

<style></style>
