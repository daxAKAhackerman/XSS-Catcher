<template>
  <b-modal
    @show="getXSS()"
    @hide="cleanup()"
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
          <b>Tags:</b>
        </b-td>
        <b-td
          ><b-badge variant="info" v-for="tag in data.tags" :key="tag">{{
            tag
          }}</b-badge></b-td
        >
      </b-tr>
      <b-tr>
        <b-td valign="top">
          <b>HTTP headers:</b>
        </b-td>
        <b-td>
          <div v-highlight>
            <pre
              class="language-http"
            ><code :key="componentKey"><div v-for="(header_value, header_name) in data.headers" v-bind:key="header_name">{{ header_name }}: {{ header_value }}</div></code></pre>
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
              <h3>{{ data_name }}</h3>
              <p>
                <a href="#" v-b-toggle="'collapse-screenshot'"
                  >[Click to view screenshot...]</a
                >
                <b-collapse
                  id="collapse-screenshot"
                  @hidden="cleanSpecificData(data_name)"
                  @show="getSpecificData(data_name)"
                >
                  <img
                    :key="componentKey"
                    style="max-width: 100%"
                    :src="data_value"
                  />
                </b-collapse>
              </p>
              <p></p>
            </div>
            <div v-else-if="data_name == 'fingerprint'">
              <h3>{{ data_name }}</h3>
              <p>
                <a href="#" v-b-toggle="'collapse-fingerprint'"
                  >[Click to view fingerprint...]</a
                >
                <b-collapse
                  id="collapse-fingerprint"
                  @hidden="cleanSpecificData(data_name)"
                  @show="getSpecificData(data_name)"
                >
                  <vue-json-pretty
                    :key="componentKey"
                    :deep="2"
                    :showLength="true"
                    :data="data_value"
                  ></vue-json-pretty>
                </b-collapse>
              </p>
              <p></p>
            </div>
            <div v-else-if="data_name == 'dom'">
              <h3>{{ data_name }}</h3>
              <p>
                <a href="#" v-b-toggle="'collapse-dom'"
                  >[Click to view DOM...]</a
                >
                <b-collapse
                  @hidden="cleanSpecificData(data_name)"
                  @show="getSpecificData(data_name)"
                  id="collapse-dom"
                >
                  <div :key="componentKey" v-highlight>
                    <pre
                      class="language-html"
                    ><code>{{ data_value }}</code></pre>
                  </div>
                </b-collapse>
              </p>
              <p></p>
            </div>
            <div
              v-else-if="
                data_name == 'cookies' ||
                data_name == 'local_storage' ||
                data_name == 'session_storage'
              "
            >
              <h3>{{ data_name }}</h3>
              <div v-for="(item, key) in data_value" v-bind:key="key">
                <code>{{ key }} => {{ item }}</code>
              </div>
              <p></p>
            </div>
            <div v-else>
              <h3>{{ data_name }}</h3>
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
import "vue-json-pretty/lib/styles.css";

import axios from "axios";

const basePath = "/api";

export default {
  props: ["xss_id", "client_id"],
  components: {
    VueJsonPretty,
  },
  computed: {
    converted_timestamp: {
      get() {
        return this.convertTimestamp(this.data.timestamp);
      },
    },
  },
  data() {
    return {
      data: {},
      componentKey: 0,
    };
  },
  methods: {
    convertTimestamp(timestamp) {
      let timestampLocal = moment
        .unix(timestamp)
        .format("dddd MMMM Do YYYY, h:mm:ss a");
      return timestampLocal;
    },
    getXSS() {
      const path = `${basePath}/xss/${this.xss_id}`;

      axios
        .get(path)
        .then((response) => {
          this.data = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    getSpecificData(loot_type) {
       const path = `${basePath}/xss/${this.xss_id}/data/${loot_type}`;

      axios
        .get(path)
        .then((response) => {
          if (loot_type === "fingerprint") {
            this.data["data"][loot_type] = JSON.parse(response.data.data);
          } else {
            this.data["data"][loot_type] = response.data.data;
          }
          this.componentKey += 1;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanSpecificData(loot_type) {
      this.data["data"][loot_type] = "";
      this.componentKey += 1;
    },
    cleanup() {
      this.data = {};
    },
  },
};
</script>

<style></style>
