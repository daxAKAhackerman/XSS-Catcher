<template>
  <b-modal
    size="xl"
    ref="getPayloadModal"
    id="get-payload-modal"
    title="Payload"
    hide-footer
    @hidden="cleanup()"
  >
    <div v-if="xss_payload !== ''">
      <b-form-textarea
        rows="3"
        no-auto-shrink
        readonly
        v-model="xss_payload"
      ></b-form-textarea>
      <br />
      <b-link
        v-clipboard:copy="xss_payload"
        @click="makeToast('Payload copied to clipboard. ', 'success', 'OK')"
        >Copy to clipboard</b-link
      >
      <hr />
    </div>
    <p>XSS type</p>
    <b-form-radio-group
      class="payload-double-selector"
      v-model="xss_type"
      :options="options.xss_type"
      buttons
      button-variant="outline-primary"
    ></b-form-radio-group>
    <hr />
    <p>Code type</p>
    <b-form-radio-group
      class="payload-double-selector"
      v-model="code_type"
      :options="options.code_type"
      buttons
      button-variant="outline-primary"
    ></b-form-radio-group>
    <hr />
    <p>Data to gather</p>
    <b-form-checkbox-group
      class="payload-single-selector"
      @change="all = []"
      v-model="to_gather"
      :options="options.to_gather"
      buttons
      button-variant="outline-primary"
    ></b-form-checkbox-group>
    <br />
    <br />
    <b-form-checkbox-group
      class="payload-single-selector"
      @change="to_gather = []"
      v-model="all"
      :options="options.all"
      buttons
      button-variant="outline-primary"
    ></b-form-checkbox-group>
    <hr />
    <p>Custom tags</p>
    <div v-for="(data, index) in custom_tags" :key="index">
      <b-row>
        <b-col sm="5">
          <b-form-input
            placeholder="key"
            v-model="data.key"
            name="input"
          ></b-form-input>
        </b-col>
        <b-col sm="5">
          <b-form-input
            placeholder="value"
            v-model="data.value"
            name="input"
          ></b-form-input>
        </b-col>
        <b-col sm="2">
          <b-button
            block
            variant="outline-danger"
            @click="custom_tags.splice(index, 1)"
            >-</b-button
          >
        </b-col>
      </b-row>
      <br />
    </div>
    <b-button
      block
      variant="outline-success"
      @click="custom_tags.push({ key: '', value: '' })"
      >+</b-button
    >
    <br />
    <div class="text-right">
      <b-button @click="getPayload()" variant="outline-info">Generate</b-button>
      <b-button @click="cleanup()" variant="outline-secondary">Cancel</b-button>
    </div>
  </b-modal>
</template>

<script>
import axios from "axios";

const basePath = "/api";

export default {
  props: ["client_id"],
  data() {
    return {
      options: {
        to_gather: [
          { text: "Local storage", value: "local_storage" },
          { text: "Session storage", value: "session_storage" },
          { text: "Cookies", value: "cookies" },
          { text: "Origin URL", value: "origin_url" },
          { text: "Referrer", value: "referrer" },
          { text: "DOM", value: "dom" },
          { text: "Screenshot", value: "screenshot" },
          { text: "Fingerprint", value: "fingerprint" },
        ],
        xss_type: [
          { text: "Stored", value: "s" },
          { text: "Reflected", value: "r" },
        ],
        code_type: [
          { text: "HTML", value: "html" },
          { text: "JavaScript", value: "js" },
        ],
        all: [{ text: "All of the above", value: "all" }],
      },
      to_gather: [],
      all: [],
      xss_type: "s",
      code_type: "html",
      xss_payload: "",
      custom_tags: [],
    };
  },
  methods: {
    getPayload() {
      const path = `${basePath}/xss/generate`;
      let payload = {
        url: location.origin,
        code_type: this.code_type,
        xss_type: this.xss_type,
        client_id: this.client_id,
        to_gather: this.to_gather,
        custom_tags: this.custom_tags,
      };

      if (this.all.includes("all")) {
        payload.to_gather = [
          "local_storage",
          "session_storage",
          "cookies",
          "origin_url",
          "referrer",
          "dom",
          "screenshot",
          "fingerprint",
        ];
      }

      axios
        .post(path, payload)
        .then((response) => {
          this.xss_payload = response.data.detail;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanup() {
      this.to_gather = [];
      this.all = [];
      this.xss_type = "stored";
      this.code_type = "html";
      this.xss_payload = "";
      this.custom_tags = [];

      this.$refs.getPayloadModal.hide();
      this.$emit("get-clients");
    },
  },
};
</script>

<style>
.payload-single-selector {
  width: 100%;
}

.payload-double-selector {
  width: 100%;
}

.payload-double-selector label {
  width: 50%;
}

.btn-outline-primary:not(:disabled):not(.disabled):active,
.btn-outline-primary:not(:disabled):not(.disabled).active,
.show > .btn-outline-primary.dropdown-toggle {
  background-color: #5bc0de !important;
}
</style>
