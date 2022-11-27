<template>
  <b-row>
    <b-col sm="3" class="text-left">
      <b-button
        v-b-modal.add-client-modal
        type="button"
        variant="outline-success"
      >
        Add new client
      </b-button>
    </b-col>
    <b-col offset-sm="1" sm="8" class="text-right">
      <b-button
        variant="outline-secondary"
        v-b-tooltip.hover
        title="Refresh data"
        @click="$emit('get-clients', true)"
      >
        <b-icon-arrow-repeat
          style="width: 20px; height: 20px"
        ></b-icon-arrow-repeat>
      </b-button>
      <b-button
        v-if="user_is_admin"
        variant="outline-info"
        v-b-modal.manage-users-modal
        >Manage users</b-button
      >
      <b-button variant="outline-warning" v-b-modal.change-password-modal
        >Change password</b-button
      >
      <b-button type="button" variant="outline-warning" @click="$emit('logout')"
        >Log out</b-button
      >
    </b-col>
  </b-row>
</template>

<script>
export default {
  props: ["user_is_admin"],
};
</script>
<style>
</style>
