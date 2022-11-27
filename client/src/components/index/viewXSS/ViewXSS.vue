<template>
  <b-modal
    ref="viewXSSModal"
    id="view-XSS-modal"
    title="Triggered XSS"
    hide-footer
    size="lg"
    @show="getXSSList()"
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
    <br />
    <b-table
      :filterIncludedFields="filterOn"
      @filtered="onFiltered"
      :current-page="currentPage"
      :per-page="perPage"
      :sort-by.sync="sortBy"
      :items="dataXSS"
      :fields="fields"
      :filter="search"
      :sort-desc.sync="sortDesc"
      :sort-direction="sortDirection"
      hover
    >
      <template v-slot:cell(timestamp)="row">{{
        convertTimestamp(row.item.timestamp)
      }}</template>
      <template v-slot:cell(tags)="row">
          <b-badge variant="info" v-for="tag in row.item.tags" :key="tag">{{tag}}</b-badge>
      </template>
      <template v-slot:cell(action)="row">
        <b-button
          type="button"
          variant="outline-info"
          v-b-modal.view-details-modal
          @click="xss_id = row.item.id"
          >View details</b-button
        >
        <b-button
          v-if="owner_id === user_id || is_admin"
          v-b-tooltip.hover
          title="Delete XSS"
          @click="to_delete = row.item.id"
          v-b-modal.delete-xss-modal
          type="button"
          variant="outline-danger"
        >
          <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
        </b-button>
      </template>
    </b-table>

    <b-row>
      <b-col sm="3">
        <b-pagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage"
        ></b-pagination>
      </b-col>
      <b-col offset-sm="6" sm="3">
        <b-form-select
          size="sm"
          v-model="perPage"
          :options="[
            { value: 5, text: '-- Per page --' },
            { value: 5, text: '5' },
            { value: 10, text: '10' },
            { value: 25, text: '25' },
          ]"
          >-- Per page --</b-form-select
        >
      </b-col>
    </b-row>

    <DeleteXSS :to_delete="to_delete" @get-xss-list="getXSSList" />

    <ViewDetails :xss_id="xss_id" :client_id="client_id" />
  </b-modal>
</template>

<script>
import axios from "axios";
import Vue2Filters from "vue2-filters";

import ViewDetails from "../shared/ViewDetails";
import DeleteXSS from "./DeleteXSS";
import moment from "moment";

const basePath = "/api";

export default {
  components: {
    ViewDetails,
    DeleteXSS,
  },
  props: ["xss_type", "client_id", "is_admin", "owner_id", "user_id"],
  mixins: [Vue2Filters.mixin],
  data() {
    return {
      fields: [
        {
          key: "formattedTimestamp",
          sortable: true,
          label: "Timestamp",
        },
        {
          key: "ip_addr",
          sortable: true,
          label: "IP address",
        },
        {
            key: "tags",
            sortable: false,
            label: "Tags"
        },
        {
          key: "action",
          sortable: false,
          label: "Action",
          class: "text-right",
        },
      ],
      sortBy: "formattedTimestamp",
      sortDesc: true,
      sortDirection: "desc",
      dataXSS: [],
      xss_id: 0,
      to_delete: 0,
      perPage: 5,
      currentPage: 1,
      totalRows: 0,
      search: "",
      filterOn: ["formattedTimestamp", "ip_addr", "tags"],
    };
  },
  methods: {
    getXSSList() {
      const path = `${basePath}/xss`;

      const payload = {
        client_id: this.client_id,
        type: this.xss_type,
      };

      axios
        .get(path, { params: payload })
        .then((response) => {
          this.dataXSS = response.data;
          for (const index in this.dataXSS) {
            this.dataXSS[index].formattedTimestamp = this.convertTimestamp(
              this.dataXSS[index].timestamp
            );
          }
          this.totalRows = this.dataXSS.length;
        })
        .catch((error) => {
          this.handleError(error);
        });
    },
    convertTimestamp(timestamp) {
      let timestampLocal = moment
        .unix(timestamp)
        .format("YYYY-MM-DD @ HH:mm:ss");
      return timestampLocal;
    },
    onFiltered(filteredItems) {
      this.totalRows = filteredItems.length;
    },
    cleanup() {
      this.dataXSS = [];
      this.xss_id = 0;
      this.to_delete = 0;
      this.$emit("get-clients");
    },
  },
};
</script>

<style></style>
