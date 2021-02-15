<template>
  <b-row>
    <b-col sm="9" class="text-left">
      <img height="75px" src="../../assets/images/logo.png" />
      <img height="40px" src="../../assets/images/title.png" />
    </b-col>
    <b-col sm="3" class="text-right">
      <p v-if="user.is_admin" style="margin-bottom: 0; margin-top: revert">
        Current user:
        <b>{{ user.username }}</b
        >&nbsp;
        <b-link v-b-modal.settings-modal>
          <b-icon-gear></b-icon-gear>
        </b-link>
      </p>
      <p v-else style="margin-bottom: 0; margin-top: revert">
        Current user:
        <b>{{ user.username }}</b>
      </p>
    </b-col>
  </b-row>
</template>
<script>
export default {
  props: ["user"],
};
</script>
<style>
</style>
