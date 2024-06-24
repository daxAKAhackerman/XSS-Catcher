<template>
  <b-navbar toggleable="lg" type="dark">
    <b-navbar-brand href="#">
      <img height="50px" src="../../assets/images/logo.png" />
      <img class="ml-2" height="35px" src="../../assets/images/title.png" />
    </b-navbar-brand>
    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto xss-navbar-links">
        <b-nav-item v-if="user.is_admin" v-b-modal.manage-users-modal>Users</b-nav-item>
        <b-nav-item v-if="user.is_admin" v-b-modal.settings-modal>Settings</b-nav-item>
        <b-nav-item-dropdown :text="user.username" right>
          <b-dropdown-item v-b-modal.security-modal>Password and authentication</b-dropdown-item>
          <b-dropdown-item @click="$emit('logout')">Logout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>
<script>
export default {
  props: ["user"],
};
</script>
<style>
.nav-link.dropdown-toggle {
  font-weight: bold !important;
}
</style>
