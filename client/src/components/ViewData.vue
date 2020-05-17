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
                <b-collapse :id="'collapse-img-' + String(Object.keys(row.item)[0])">
                  <img style="max-width:100%" :src="Object.values(row.item)[0]" />
                </b-collapse>
              </p>
            </div>
            <div v-else-if="element_name == 'fingerprint'">
              <p>
                <vue-json-pretty :deep="0" :showLength="true" :data="Object.values(row.item)[0]"></vue-json-pretty>
              </p>
            </div>
            <div v-else-if="element_name == 'dom'">
              <p>
                <a
                  href="#"
                  v-b-toggle="'collapse-dom-' + String(Object.keys(row.item)[0])"
                >[Click to view DOM...]</a>
                <b-collapse :id="'collapse-dom-' + String(Object.keys(row.item)[0])">
                  <div v-highlight>
                    <pre class="language-html"><code>{{ Object.values(row.item)[0] }}</code></pre>
                  </div>
                </b-collapse>
              </p>
            </div>
            <div
              v-else-if="element_name == 'cookies' || element_name == 'local_storage' || element_name == 'session_storage'"
            >
              <div v-for="(value, param) in row.item" v-bind:key="param">
                <div
                  v-for="(value_deep, param_deep) in Object.values(value)[0]"
                  v-bind:key="param_deep"
                >
                  <code>{{ param_deep }} => {{ value_deep }}</code>
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
      <b-form @submit="deleteData" @reset="$refs.deleteDataModal.hide()">
        <b-button type="submit" variant="outline-danger">Yes, delete this entry</b-button>
        <b-button type="reset" variant="outline-secondary">Cancel</b-button>
      </b-form>
    </b-modal>
  </b-modal>
</template>

<script>
import axios from "axios";
import VueJsonPretty from "vue-json-pretty";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  props: ["client_id", "is_admin", "owner_id", "user_id"],
  components: {
    VueJsonPretty
  },
  data() {
    return {
      fields: [
        {
          key: "data",
          class: "text-left width90"
        },
        {
          key: "action",
          class: "text-right"
        }
      ],
      data: {},
      to_delete: 0,
      to_delete_type: "",
      search: "",
      componentKey: 0
    };
  },
  methods: {
    getData() {
      const path = basePath + "/client/" + this.client_id + "/loot";

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
    deleteData() {
      const path =
        basePath + "/xss/" + this.to_delete + "/" + this.to_delete_type;

      axios
        .delete(path)
        .then(response => {
          void response;
          this.getData();
          this.$refs.deleteDataModal.hide();
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
      this.to_delete = 0;
      this.to_delete_type = "";
      this.$parent.getClients();
    }
  }
};
</script>

<style>
.width90 {
  width: 90%;
}
.invisible {
  display: none;
}
</style>
