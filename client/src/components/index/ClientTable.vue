<template>
  <div>
    <b-row align-v="center" class="align-items-center">
      <b-col sm="2">
        <b-button v-b-modal.add-client-modal type="button" variant="outline-success">
          Add new client
        </b-button>
      </b-col>
      <b-col offset-sm="5" sm="3">
        <b-input-group>
          <b-form-input size="sm" v-model="search" type="search" placeholder="Search"></b-form-input>
          <b-input-group-append>
            <b-button variant="outline-secondary" size="sm" :disabled="!search" @click="search = ''">Clear</b-button>
          </b-input-group-append>
        </b-input-group>
      </b-col>
      <b-col class="ml-auto d-flex">
        <div class="d-flex align-items-center ml-auto">
          Rows per page
          <div class="row-per-page-select ml-2">
            <b-form-select size="sm" v-model="perPage" :options="[
            { value: 5, text: '5' },
            { value: 10, text: '10' },
            { value: 25, text: '25' },
          ]"></b-form-select>
          </div>
          <b-icon-arrow-repeat v-b-tooltip.hover title="Refresh data" @click="$emit('get-clients', true)"
            style="width: 20px; height: 20px" class="clickable-icon ml-2"></b-icon-arrow-repeat>
        </div>
      </b-col>
    </b-row>
    <br />
    <b-row>
      <b-table @filtered="onFiltered" :current-page="currentPage" :per-page="perPage" :items="clients" :fields="fields"
        :filter="search" :filter-included-fields="filterFields" hover>
        <template v-slot:cell(name)="row">
          <b-link @click="$emit('view-client', row.item)" v-b-modal.view-client-modal>{{ row.item.name }}</b-link>
        </template>
        <template v-slot:cell(stored)="row">
          <b-link @click="$emit('view-stored', row.item)" v-b-modal.view-XSS-modal>{{ row.item.stored }}</b-link>
        </template>
        <template v-slot:cell(reflected)="row">
          <b-link @click="$emit('view-reflected', row.item)" v-b-modal.view-XSS-modal>{{ row.item.reflected }}</b-link>
        </template>
        <template v-slot:cell(data)="row">
          <b-link @click="$emit('view-data', row.item)" v-b-modal.view-data-modal>{{ row.item.data }}</b-link>
        </template>
        <template v-slot:cell(action)="row">
          <b-button @click="$emit('generate-payload', row.item)" v-b-modal.get-payload-modal type="button"
            variant="outline-success">Generate payload</b-button>
          <b-button v-if="row.item.owner_id === user.id || user.is_admin" v-b-tooltip.hover title="Delete client"
            @click="$emit('delete-client', row.item.id)" v-b-modal.delete-client-modal type="button"
            variant="outline-danger">
            <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
          </b-button>
          <b-button v-else disabled type="button" variant="outline-danger">
            <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
          </b-button>
        </template>
      </b-table>
    </b-row>
    <b-row>
      <b-col>
        <b-pagination class="mt-0 mb-0" v-model="currentPage" :total-rows="totalRows"
          :per-page="perPage"></b-pagination>
      </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
  props: ["clients", "totalRows", "user"],
  data() {
    return {
      fields: [
        {
          key: "name",
          sortable: true,
          label: "Client name",
        },
        {
          key: "stored",
          sortable: true,
          label: "Stored XSS",
        },
        {
          key: "reflected",
          sortable: true,
          label: "Reflected XSS",
        },
        {
          key: "data",
          sortable: true,
          label: "Data collected",
        },
        {
          key: "action",
          sortable: false,
          label: "",
          tdClass: "text-right"
        },
      ],
      perPage: 5,
      currentPage: 1,
      search: "",
      filterFields: ["name"],
    };
  },
  methods: {
    onFiltered(filteredItems) {
      this.$emit("set-total-rows", filteredItems.length);
    },
  },
};
</script>

<style scoped>
.clickable-icon {
  cursor: pointer;
}

.row-per-page-select select {
  width: 60px;
}
</style>
