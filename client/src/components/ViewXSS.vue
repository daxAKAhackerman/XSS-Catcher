<template>
  <b-modal
    ref="viewXSSModal"
    id="view-XSS-modal"
    title="Triggered XSS"
    hide-footer
    size="lg"
    @show="getXSS"
    @hide="cleanup"
  >
    <b-table :sort-by.sync="sortBy" :items="dataXSS" :fields="fields" hover>
      <template v-slot:cell(timestamp)="row">{{ convertTimestamp(row.item.timestamp) }}</template>
      <template class="text-right" v-slot:cell(action)="row">
        <b-button
          type="button"
          variant="info"
          v-b-modal.view-details-modal
          @click="viewedXSS=row.item"
        >View details</b-button>
        <b-button
          v-if="owner_id === user_id || is_admin"
          v-b-tooltip.hover
          title="Delete XSS"
          @click="to_delete = row.item.id"
          v-b-modal.delete-xss-modal
          type="button"
          variant="danger"
        >
          <b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
        </b-button>
      </template>
    </b-table>

    <b-modal ref="deleteXSSModal" id="delete-xss-modal" title="Are you sure?" hide-footer>
      <b-form @submit="deleteXSS" @reset="$refs.deleteXSSModal.hide()">
        <b-button type="submit" variant="danger">Yes, delete this entry</b-button>
        <b-button type="reset">Cancel</b-button>
      </b-form>
    </b-modal>

    <ViewDetails :data="viewedXSS" />
  </b-modal>
</template>

<script>
import axios from "axios";
import Vue2Filters from "vue2-filters";

import ViewDetails from "./ViewDetails";
import moment from "moment";

axios.defaults.headers.post["Content-Type"] =
  "application/x-www-form-urlencoded";

const basePath = "/api";

export default {
  components: {
    ViewDetails
  },
  props: ["xss_type", "client_id", "is_admin", "owner_id", "user_id"],
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      fields: [
        {
          key: "timestamp",
          sortable: true,
          label: "Timestamp",
          sortDirection: "desc"
        },
        {
          key: "ip_addr",
          sortable: true,
          label: "IP address"
        },
        {
          key: "action",
          sortable: false,
          label: "Action",
          class: "text-right"
        }
      ],
      sortBy: "timestamp",
      dataXSS: {},
      viewedXSS: {},
      to_delete: 0
    };
  },
  methods: {
    getXSS() {
      const path = basePath + "/client/" + this.client_id + "/" + this.xss_type;

      axios
        .get(path)
        .then(response => {
          this.dataXSS = response.data;
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    deleteXSS() {
      const path = basePath + "/xss/" + this.to_delete;

      axios
        .delete(path)
        .then(response => {
          void response;
          this.getXSS();
          this.$refs.deleteXSSModal.hide();
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$router.push({ name: "Login" });
          } else {
            void error;
          }
        });
    },
    convertTimestamp(timestamp) {
      let timestampLocal = moment(timestamp).format("YYYY-MM-DD @ HH:mm:ss");
      return timestampLocal;
    },
    cleanup() {
      this.dataXSS = {};
      this.viewedXSS = {};
      this.to_delete = 0;
      this.$parent.getClients();
    }
  }
};
</script>

<style></style>
