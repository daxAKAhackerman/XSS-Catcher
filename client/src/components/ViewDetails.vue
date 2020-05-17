<template>
  <b-modal
    @show="getXSS"
    @hide="cleanup"
    ref="viewDetailsModal"
    id="view-details-modal"
    title="Details"
    hide-footer
    size="xl"
  >
    <b-table-simple style="table-layout: fixed; width: 100%">
      <b-tr>
        <b-td valign="top">
          <b>Timestamp:</b>
        </b-td>
        <b-td width="80%">{{ converted_timestamp }}</b-td>
      </b-tr>
      <b-tr>
        <b-td valign="top">
          <b>IP address:</b>
        </b-td>
        <b-td>{{ data.ip_addr }}</b-td>
      </b-tr>
      <b-tr>
        <b-td valign="top">
          <b>HTTP headers:</b>
        </b-td>
        <b-td>
          <div v-highlight>
            <pre class="language-http"><code><div v-for="(header_value, header_name) in data.headers" v-bind:key="header_name"><div
  v-for="(header_value_deep, header_name_deep) in header_value"
  v-bind:key="header_name_deep"
>{{ header_name_deep }}: {{ header_value_deep }}
</div></div></code></pre>
          </div>
        </b-td>
      </b-tr>
      <b-tr>
        <b-td valign="top">
          <b>Captured data:</b>
        </b-td>
        <b-td>
          <div
            v-for="(data_value, data_name) in data.data"
            v-bind:key="data_name"
            style="word-wrap: break-word"
          >
            <div v-if="data_name == 'screenshot'">
              <h4>{{ data_name }}</h4>
              <p>
                <a href="#" v-b-toggle="'collapse-screenshot'">[Click to view screenshot...]</a>
                <b-collapse id="collapse-screenshot">
                  <img style="max-width:100%" :src="data_value" />
                </b-collapse>
              </p>
              <p></p>
            </div>
            <div v-else-if="data_name == 'fingerprint'">
              <h4>{{ data_name }}</h4>
              <p>
                <vue-json-pretty :deep="0" :showLength="true" :data="data_value"></vue-json-pretty>
              </p>
              <p></p>
            </div>
            <div v-else-if="data_name == 'dom'">
              <h4>{{ data_name }}</h4>
              <p>
                <a href="#" v-b-toggle="'collapse-dom'">[Click to view DOM...]</a>
                <b-collapse id="collapse-dom">
                  <div v-highlight>
                    <pre class="language-html"><code>{{ data_value }}</code></pre>
                  </div>
                </b-collapse>
              </p>
              <p></p>
            </div>
            <div
              v-else-if="data_name == 'cookies' || data_name == 'local_storage' || data_name == 'session_storage'"
            >
              <h4>{{ data_name }}</h4>
              <div v-for="(value, param) in data_value" v-bind:key="param">
                <div v-for="(value_deep, param_deep) in value" v-bind:key="param_deep">
                  <code>{{ param_deep }} => {{ value_deep }}</code>
                </div>
              </div>
              <p></p>
            </div>
            <div v-else>
              <h4>{{ data_name }}</h4>
              <p>
                <code>{{ data_value }}</code>
              </p>
              <p></p>
            </div>
          </div>
        </b-td>
      </b-tr>
    </b-table-simple>
  </b-modal>
</template>

<script>
import moment from "moment";
import VueJsonPretty from "vue-json-pretty";

import axios from "axios";

const basePath = "/api";

export default {
  props: ["xss_id", "xss_type", "client_id"],
  components: {
    VueJsonPretty
  },
  computed: {
    converted_timestamp: {
      get() {
        return this.convertTimestamp(this.data.timestamp);
      }
    }
  },
  data() {
    return {
      data: {}
    };
  },
  methods: {
    convertTimestamp(timestamp) {
      let timestampLocal = moment(timestamp).format(
        "dddd MMMM Do YYYY, h:mm:ss a"
      );
      return timestampLocal;
    },
    getXSS() {
      const path =
        basePath +
        "/client/" +
        this.client_id +
        "/" +
        this.xss_type +
        "/" +
        this.xss_id;

      axios
        .get(path)
        .then(response => {
          this.data = response.data;
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    cleanup() {
      this.data = {};
    }
  }
};
</script>

<style></style>
