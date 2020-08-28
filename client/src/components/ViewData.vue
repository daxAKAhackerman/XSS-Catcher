<template>
  <b-modal
    ref="viewDataModal"
    id="view-data-modal"
    title="Captured data"
    hide-footer
    size="xl"
    @show="getData"
    @hide="cleanup"
  >
    <b-row>
      <b-col offset-sm="8" sm="4">
        <b-input-group>
          <b-form-input size="sm" v-model="search" type="search" placeholder="Search"></b-form-input>
          <b-input-group-append>
            <b-button
              variant="outline-secondary"
              size="sm"
              :disabled="!search"
              @click="search = ''"
            >Clear</b-button>
          </b-input-group-append>
        </b-input-group>
      </b-col>
    </b-row>
    <div v-for="(element_value, element_name) in data" v-bind:key="element_name">
      <h4>{{ element_name }}</h4>

      <b-table
        :fields="fields"
        :items="data[element_name]"
        :filter="search"
        hover
        style="table-layout: fixed; width: 100%"
        thead-class="invisible"
      >
        <template v-slot:cell(data)="row">
          <div style="word-wrap: break-word">
            <div v-if="element_name == 'screenshot'">
              <p>
                <a
                  href="#"
                  v-b-toggle="'collapse-img-' + String(Object.keys(row.item)[0])"
                >[Click to view screenshot...]</a>
                <b-collapse
                  @hidden="cleanSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  @show="getSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  :id="'collapse-img-' + String(Object.keys(row.item)[0])"
                >
                  <img :key="componentKey" style="max-width:100%" :src="Object.values(row.item)[0]" />
                </b-collapse>
              </p>
            </div>
            <div v-else-if="element_name == 'fingerprint'">
              <p>
                <a
                  href="#"
                  v-b-toggle="'collapse-fingerprint-' + String(Object.keys(row.item)[0])"
                >[Click to view fingerprint...]</a>
                <b-collapse
                  @hidden="cleanSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  @show="getSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  :id="'collapse-fingerprint-' + String(Object.keys(row.item)[0])"
                >
                  <vue-json-pretty
                    :key="componentKey"
                    :deep="2"
                    :showLength="true"
                    :data="Object.values(row.item)[0]"
                  ></vue-json-pretty>
                </b-collapse>
              </p>
            </div>
            <div v-else-if="element_name == 'dom'">
              <p>
                <a
                  href="#"
                  v-b-toggle="'collapse-dom-' + String(Object.keys(row.item)[0])"
                >[Click to view DOM...]</a>
                <b-collapse
                  @hidden="cleanSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  @show="getSpecificData(String(Object.keys(row.item)[0]), element_name, row.index)"
                  :id="'collapse-dom-' + String(Object.keys(row.item)[0])"
                >
                  <div :key="componentKey" v-highlight>
                    <pre class="language-html"><code>{{ Object.values(row.item)[0] }}</code></pre>
                  </div>
                </b-collapse>
              </p>
            </div>
            <div
              v-else-if="element_name == 'cookies' || element_name == 'local_storage' || element_name == 'session_storage'"
            >
              <div v-for="(value, param) in row.item" v-bind:key="param">
                <div v-for="(value_deep, param_deep) in value" v-bind:key="param_deep">
                  <code>{{ Object.keys(value_deep)[0] }} => {{ Object.values(value_deep)[0] }}</code>
                </div>
              </div>
            </div>
            <div v-else>
              <p>
                <code>{{ Object.values(row.item)[0] }}</code>
              </p>
            </div>
          </div>
        </template>
        <template v-slot:cell(action)="row">
          <b-button
            type="button"
            v-b-tooltip.hover
            title="View details"
            variant="outline-info"
            v-b-modal.view-details-modal
            @click="xss_detail_id=String(Object.keys(row.item)[0])"
          >
            <b-icon-info style="width: 20px; height: 20px;"></b-icon-info>
          </b-button>
          <b-button
            v-if="owner_id === user_id || is_admin"
            v-b-tooltip.hover
            title="Delete data"
            @click="to_delete_type = element_name; to_delete = Object.keys(row.item)[0]"
            v-b-modal.delete-data-modal
            type="button"
            variant="outline-danger"
          >
            <b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
          </b-button>
        </template>
      </b-table>
    </div>

    <b-modal ref="deleteDataModal" id="delete-data-modal" title="Are you sure?" hide-footer>
      <b-form>
        <b-button @click="deleteData" variant="outline-danger">Yes, delete this entry</b-button>
        <b-button @click="$refs.deleteDataModal.hide()" variant="outline-secondary">Cancel</b-button>
      </b-form>
    </b-modal>

    <ViewDetails :xss_id="xss_detail_id" :client_id="client_id" />
  </b-modal>
</template>

<script>
import axios from "axios";
import VueJsonPretty from "vue-json-pretty";
import ViewDetails from "./ViewDetails";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  props: ["client_id", "is_admin", "owner_id", "user_id"],
  components: {
    VueJsonPretty,
    ViewDetails,
  },
  data() {
    return {
      fields: [
        {
          key: "data",
          class: "text-left width88",
        },
        {
          key: "action",
          class: "text-right",
        },
      ],
      data: {},
      to_delete: 0,
      to_delete_type: "",
      search: "",
      componentKey: 0,
      xss_detail_id: 0,
    };
  },
  methods: {
    getData() {
      const path = basePath + "/client/" + this.client_id + "/loot";

      axios
        .get(path)
        .then((response) => {
          this.data = response.data;
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
    deleteData() {
      const path =
        basePath + "/xss/" + this.to_delete + "/" + this.to_delete_type;

      axios
        .delete(path)
        .then((response) => {
          this.makeToast(response.data.detail, "success", response.data.status);
          this.getData();
          this.$refs.deleteDataModal.hide();
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
    getSpecificData(element_id, loot_type, row_index) {
      const path = basePath + "/xss/" + element_id + "/" + loot_type;

      axios
        .get(path)
        .then((response) => {
          if (loot_type === "fingerprint") {
            this.data[loot_type][row_index][element_id] = JSON.parse(
              response.data.data
            );
          } else {
            this.data[loot_type][row_index][element_id] = response.data.data;
          }
          this.componentKey += 1;
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
    cleanSpecificData(element_id, loot_type, row_index) {
      this.data[loot_type][row_index][element_id] = "";
      this.componentKey += 1;
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
      this.data = {};
      this.to_delete = 0;
      this.to_delete_type = "";
      this.$parent.getClients();
    },
  },
};
</script>

<style>
.width88 {
  width: 88%;
}
.invisible {
  display: none;
}
</style>
