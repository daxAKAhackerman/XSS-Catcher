<template>
  <b-modal
    size="md"
    ref="getPayloadModal"
    id="get-payload-modal"
    title="Payload"
    hide-footer
    @hidden="cleanup"
  >
    <b-form v-on:submit.prevent>
      <b-form-group class="text-left">
        <div v-if="xss_payload !== ''">
          <b-form-group>
            <b-form-textarea rows="3" no-auto-shrink readonly v-model="xss_payload"></b-form-textarea>
            <br />
            <b-link
              v-clipboard:copy="xss_payload"
              @click="makeToast('Payload copied to clipboard. ', 'success', 'OK')"
            >Copy to clipboard</b-link>
          </b-form-group>
          <hr />
        </div>
        <b-form-group label="XSS type: ">
          <b-form-radio-group
            v-model="options.stored"
            :options="options.typeList"
            buttons
            button-variant="outline-primary"
          ></b-form-radio-group>
        </b-form-group>
        <hr />
        <b-form-group label="Gather data: ">
          <b-form-checkbox-group
            @change="options.gatherAll=[]"
            v-model="options.gatherData"
            :options="options.gatherDataList"
            buttons
            button-variant="outline-primary"
          ></b-form-checkbox-group>
          <br />
          <br />
          <b-form-checkbox-group
            @change="options.gatherData=[]"
            v-model="options.gatherAll"
            :options="options.gatherAllList"
            buttons
            button-variant="outline-primary"
          ></b-form-checkbox-group>
        </b-form-group>
        <hr />
        <b-form-group label="Code type: ">
          <b-form-radio-group
            v-model="options.code_type"
            :options="options.codeTypeList"
            buttons
            button-variant="outline-primary"
          ></b-form-radio-group>
        </b-form-group>
        <hr />
      </b-form-group>

      <b-form-group label="Other data: ">
        <b-form-input
          @keyup.enter="getPayload"
          v-model="options.other"
          name="input"
          label="Other data: "
          placeholder="param1=value1&param2=value2"
        ></b-form-input>
      </b-form-group>
      <div class="text-right">
        <b-button @click="getPayload" variant="outline-info">Generate</b-button>
        <b-button @click="cleanup" variant="outline-secondary">Cancel</b-button>
      </div>
    </b-form>
  </b-modal>
</template>

<script>
import axios from "axios";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  props: ["client_id"],
  data() {
    return {
      options: {
        gatherData: [],
        gatherAll: [],
        gatherDataList: [
          { text: "Local storage", value: "local_storage" },
          { text: "Session storage", value: "session_storage" },
          { text: "Cookies", value: "cookies" },
          { text: "Origin URL", value: "geturl" },
        ],
        typeList: [
          { text: "Reflected", value: false },
          { text: "Stored", value: true },
        ],
        codeTypeList: [
          { text: "HTML", value: "html" },
          { text: "JavaScript", value: "js" },
        ],
        gatherAllList: [
          {
            text: "All of the above + screenshot/fingerprint/DOM",
            value: "all",
          },
        ],
        stored: false,
        code_type: "html",
        other: "",
      },
      xss_payload: "",
    };
  },
  methods: {
    getPayload() {
      let path =
        basePath +
        "/xss/generate/" +
        this.client_id +
        "?url=" +
        encodeURIComponent(location.origin) +
        "&";

      if (this.options.gatherAll.includes("all")) {
        path += "i_want_it_all=1&";
      }

      if (this.options.gatherData.includes("cookies")) {
        path += "cookies=1&";
      }

      if (this.options.gatherData.includes("local_storage")) {
        path += "local_storage=1&";
      }

      if (this.options.gatherData.includes("session_storage")) {
        path += "session_storage=1&";
      }

      if (this.options.stored) {
        path += "stored=1&";
      }

      if (this.options.gatherData.includes("geturl")) {
        path += "geturl=1&";
      }

      if (this.options.other) {
        path += this.options.other + "&";
      }

      path += "code=" + this.options.code_type;

      if (path.substr(-1) === "&") {
        path = path.substr(0, path.length - 1);
      }

      axios
        .get(path)
        .then((response) => {
          this.xss_payload = response.data;
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            this.makeToast(
              error.response.data.detail,
              "danger",
              error.response.data.status
            );
          }
        });
    },
    makeToast(message, variant, title) {
      this.$root.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: variant,
      });
    },
    cleanup() {
      this.xss_payload = "";
      this.options.gatherData = [];
      this.options.stored = false;
      this.options.code_type = "html";
      this.options.other = "";

      this.$refs.getPayloadModal.hide();
      this.$parent.getClients();
    },
  },
};
</script>

<style>
.btn-outline-primary:not(:disabled):not(.disabled):active,
.btn-outline-primary:not(:disabled):not(.disabled).active,
.show > .btn-outline-primary.dropdown-toggle {
  background-color: #5bc0de !important;
}
</style>
