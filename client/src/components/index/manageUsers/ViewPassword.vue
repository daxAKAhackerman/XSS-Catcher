<template>
  <b-modal
    ref="viewPasswordModal"
    id="view-password-modal"
    title="User created"
    hide-footer
    @hide="cleanup()"
  >
    <p>Username: {{ username }}</p>
    <p>Password: {{ password }}</p>
    <div class="text-right">
      <b-button @click="cleanup()" variant="outline-secondary">Close</b-button>
    </div>
  </b-modal>
</template>
<script>
export default {
  props: ["username", "password"],
  methods: {
    cleanup() {
      this.$refs.viewPasswordModal.hide();
      this.$emit("cleanup");
    },
  },
};
</script>

<style></style>
