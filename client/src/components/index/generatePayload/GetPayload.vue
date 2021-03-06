<template>
  <b-modal
    size=""
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
      stacked
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
    <p>Additionnal parameters</p>
    <div v-for="data in other_data" :key="data.id">
      <b-row>
        <b-col sm="4">
          <b-form-input v-model="data.key" name="input"></b-form-input>
        </b-col>
        <b-col sm="4">
          <b-form-input v-model="data.value" name="input"></b-form-input>
        </b-col>
        <b-col sm="2">
          <b-button
            @click="other_data.push({ id: data.id + 1, key: '', value: '' })"
            >+</b-button
          >
        </b-col>
        <b-col sm="2">
          <b-button>-</b-button>
        </b-col>
      </b-row>
    </div>
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
          { text: "Stored", value: "stored" },
          { text: "Reflected", value: "reflected" },
        ],
        code_type: [
          { text: "HTML", value: "html" },
          { text: "JavaScript", value: "js" },
        ],
        all: [{ text: "All of the above", value: "all" }],
      },
      to_gather: [],
      all: [],
      xss_type: "stored",
      code_type: "html",
      xss_payload: "",
      number_of_other_data: 0,
      other_data: [],
    };
  },
  methods: {
    getPayload() {
      const path = `${basePath}/xss/generate`;
      let payload = {
        url: location.origin,
        code: this.options.code_type,
        client_id: this.client_id,
      };

      if (this.options.gatherAll.includes("all")) {
        payload.i_want_it_all = 1;
      }

      if (this.options.gatherData.includes("cookies")) {
        payload.cookies = 1;
      }

      if (this.options.gatherData.includes("local_storage")) {
        payload.local_storage = 1;
      }

      if (this.options.gatherData.includes("session_storage")) {
        payload.session_storage = 1;
      }

      if (this.options.stored) {
        payload.stored = 1;
      }

      if (this.options.gatherData.includes("geturl")) {
        payload.geturl = 1;
      }

      if (this.options.other) {
        const otherDataList = this.options.other.split("&");
        let otherDataDict = {};
        for (const element of otherDataList) {
          const element_splitted = element.split("=");
          otherDataDict[element_splitted[0]] = element_splitted[1];
        }
        payload = Object.assign(payload, otherDataDict);
      }

      axios
        .get(path, { params: payload })
        .then((response) => {
          this.xss_payload = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanup() {
      this.xss_payload = "";
      this.options.gatherData = [];
      this.options.stored = false;
      this.options.code_type = "html";
      this.options.other = "";

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
