<template>

  <b-modal
    ref="viewDetailsModal"
    id="view-details-modal"
    title="Details"
    hide-footer
    size="xl"
  >
    <b-form>

      <b-form-group
        id="input-group-timestamp"
        label="Timestamp:"
        label-cols="3"
        label-for="input-field-timestamp"
      >
        <b-form-input
          id="input-field-timestamp"
          v-model="data.timestamp"
          disabled
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-referer"
        label="Referer:"
        label-cols="3"
        label-for="input-field-referer"
      >
        <b-form-input
          id="input-field-referer"
          v-model="data.referer"
          disabled
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-ip_addr"
        label="IP address:"
        label-cols="3"
        label-for="input-field-ip_addr"
      >
        <b-form-input
          id="input-field-ip_addr"
          v-model="data.ip_addr"
          disabled
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-user_agent"
        label="User agent:"
        label-cols="3"
        label-for="input-field-user_agent"
      >
        <b-form-input
          id="input-field-user_agent"
          v-model="data.user_agent"
          disabled
        ></b-form-input>
      </b-form-group>

      <b-form-group
        id="input-group-cookies"
        label="Captured cookies:"
        label-cols="3"
        label-for="input-field-cookies"
      >
        <b-form-textarea
          id="input-field-cookies"
          v-model="data.cookies"
          disabled
        ></b-form-textarea>
      </b-form-group>

      <b-form-group
        id="input-group-local_storage"
        label="Captured local storage:"
        label-cols="3"
        label-for="input-field-local_storage"
      >
        <b-form-textarea
          id="input-field-local_storage"
          v-model="data.local_storage"
          disabled
        ></b-form-textarea>
      </b-form-group>

      <b-form-group
        id="input-group-session_storage"
        label="Captured session storage:"
        label-cols="3"
        label-for="input-field-session_storage"
      >
        <b-form-textarea
          id="input-field-session_storage"
          v-model="data.session_storage"
          disabled
        ></b-form-textarea>
      </b-form-group>

      <b-form-group
        id="input-group-other_data"
        label="Other captured data:"
        label-cols="3"
        label-for="input-field-other_data"
      >
        <b-form-textarea
          id="input-field-other_data"
          v-model="data.other_data"
          disabled
        ></b-form-textarea>
      </b-form-group>

    </b-form>

  </b-modal>

</template>

<script>

export default {
  props: ['data']
}

</script>

<style></style>
