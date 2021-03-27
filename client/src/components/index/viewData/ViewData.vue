<template>
  <b-modal
    ref="viewDataModal"
    id="view-data-modal"
    title="Captured data"
    hide-footer
    size="xl"
    @show="getData()"
    @hide="cleanup()"
  >
    <b-row>
      <b-col offset-sm="8" sm="4">
        <b-input-group>
          <b-form-input
            size="sm"
            v-model="search"
            type="search"
            placeholder="Search"
          ></b-form-input>
          <b-input-group-append>
            <b-button
              variant="outline-secondary"
              size="sm"
              :disabled="!search"
              @click="search = ''"
              >Clear</b-button
            >
          </b-input-group-append>
        </b-input-group>
      </b-col>
    </b-row>
    <div
      v-for="(element_value, element_name) in dataObject"
      v-bind:key="element_name"
    >
      <h4>{{ element_name }}</h4>

      <b-table
        :fields="fields"
        :items="element_value"
        :filter="search"
        :filter-function="filterFunction"
        hover
        style="table-layout: fixed; width: 100%"
        thead-class="invisible"
      >
        <template v-slot:cell(data)="row">
          <div style="word-wrap: break-word">
            <div v-if="element_name == 'screenshot'">
              <p>
                <a href="#" v-b-toggle="`collapse-img-${row.item.xss_id}`"
                  >[Click to view screenshot...]</a
                >
                <b-collapse
                  @hidden="cleanSpecificData(row.item.xss_id, element_name)"
                  @show="getSpecificData(row.item.xss_id, element_name)"
                  :id="`collapse-img-${row.item.xss_id}`"
                >
                  <img
                    :key="componentKey"
                    style="max-width: 100%"
                    :src="row.item.data"
                  />
                </b-collapse>
              </p>
            </div>
            <div v-else-if="element_name == 'fingerprint'">
              <p>
                <a
                  href="#"
                  v-b-toggle="`collapse-fingerprint-${row.item.xss_id}`"
                  >[Click to view fingerprint...]</a
                >
                <b-collapse
                  @hidden="cleanSpecificData(row.item.xss_id, element_name)"
                  @show="getSpecificData(row.item.xss_id, element_name)"
                  :id="`collapse-fingerprint-${row.item.xss_id}`"
                >
                  <vue-json-pretty
                    :key="componentKey"
                    :deep="2"
                    :showLength="true"
                    :data="row.item.data"
                  ></vue-json-pretty>
                </b-collapse>
              </p>
            </div>
            <div v-else-if="element_name == 'dom'">
              <p>
                <a href="#" v-b-toggle="`collapse-dom-${row.item.xss_id}`"
                  >[Click to view DOM...]</a
                >
                <b-collapse
                  @hidden="cleanSpecificData(row.item.xss_id, element_name)"
                  @show="getSpecificData(row.item.xss_id, element_name)"
                  @shown="componentKey += 1"
                  :id="`collapse-dom-${row.item.xss_id}`"
                >
                  <div :key="componentKey" v-highlight>
                    <pre
                      class="language-html"
                    ><code>{{ row.item.data }}</code></pre>
                  </div>
                </b-collapse>
              </p>
            </div>
            <div
              v-else-if="
                element_name == 'cookies' ||
                element_name == 'local_storage' ||
                element_name == 'session_storage'
              "
            >
              <div
                v-for="(element_key, element_value) in row.item.data"
                v-bind:key="element_key"
              >
                <code>{{ element_key }} => {{ element_value }}</code>
              </div>
            </div>
            <div v-else>
              <p>
                <code>{{ row.item.data }}</code>
              </p>
            </div>
          </div>
        </template>
        <template v-slot:cell(tags)="row">
          <b-badge variant="info" v-for="tag in row.item.tags" :key="tag">{{
            tag
          }}</b-badge>
        </template>
        <template v-slot:cell(action)="row">
          <b-button
            type="button"
            v-b-tooltip.hover
            title="View details"
            variant="outline-info"
            v-b-modal.view-details-modal
            @click="xss_detail_id = row.item.xss_id"
          >
            <b-icon-info style="width: 20px; height: 20px"></b-icon-info>
          </b-button>
          <b-button
            v-if="owner_id === user_id || is_admin"
            v-b-tooltip.hover
            title="Delete data"
            @click="
              to_delete_type = element_name;
              to_delete = row.item.xss_id;
            "
            v-b-modal.delete-data-modal
            type="button"
            variant="outline-danger"
          >
            <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
          </b-button>
        </template>
      </b-table>
    </div>

    <DeleteData
      :to_delete="to_delete"
      :to_delete_type="to_delete_type"
      @get-data="getData"
    />
    <ViewDetails :xss_id="xss_detail_id" :client_id="client_id" />
  </b-modal>
</template>

<script>
import axios from "axios";
import VueJsonPretty from "vue-json-pretty";
import ViewDetails from "../shared/ViewDetails";
import DeleteData from "./DeleteData";

const basePath = "/api";

export default {
  props: ["client_id", "is_admin", "owner_id", "user_id"],
  components: {
    VueJsonPretty,
    ViewDetails,
    DeleteData,
  },
  data() {
    return {
      fields: [
        {
          key: "data",
          class: "text-left width75",
        },
        {
          key: "tags",
        },
        {
          key: "action",
          class: "text-right",
        },
      ],
      filterIncludeFields: ["data", "tags"],
      data: [],
      to_delete: 0,
      to_delete_type: "",
      search: "",
      componentKey: 0,
      xss_detail_id: 0,
    };
  },
  computed: {
    dataObject: function () {
      let dataObject = {};
      for (const xss of this.data) {
        for (const element in xss.data) {
          if (dataObject[element] === undefined) {
            dataObject[element] = [];
          }
          dataObject[element].push({
            xss_id: xss.xss_id,
            tags: xss.tags,
            data: xss.data[element],
          });
        }
      }
      const orderedDataObject = Object.keys(dataObject)
        .sort()
        .reduce((obj, key) => {
          obj[key] = dataObject[key];
          return obj;
        }, {});
      return orderedDataObject;
    },
  },
  methods: {
    getData() {
      const path = `${basePath}/xss/data`;

      const payload = {
        client_id: this.client_id,
      };

      axios
        .get(path, { params: payload })
        .then((response) => {
          this.data = response.data;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    getSpecificData(xss_id, loot_type) {
      const path = `${basePath}/xss/${xss_id}/data/${loot_type}`;

      axios
        .get(path)
        .then((response) => {
          for (const [i, xss] of this.data.entries()) {
            if (xss.xss_id === xss_id) {
              this.data[i].data[loot_type] =
                loot_type === "fingerprint"
                  ? JSON.parse(response.data.data)
                  : response.data.data;
            }
          }
          this.componentKey += 1;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    cleanSpecificData(xss_id, loot_type) {
      for (const [i, xss] of this.data.entries()) {
        if (xss.xss_id === xss_id) {
          this.data[i].data[loot_type] = "";
        }
      }
      this.componentKey += 1;
    },
    filterFunction(item, filter) {
      if (JSON.stringify(item.tags).includes(filter)) {
        return true;
      } else if (JSON.stringify(item.data).includes(filter)) {
        return true;
      } else {
        return false;
      }
    },
    cleanup() {
      this.data = [];
      this.to_delete = 0;
      this.to_delete_type = "";
      this.$emit("get-clients");
    },
  },
};
</script>

<style>
.width75 {
  width: 75%;
}
.invisible {
  display: none;
}
</style>
