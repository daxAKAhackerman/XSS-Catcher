<template>
    <div>
        <b-table :items="apiKeys" :fields="fields" hover>
            <template v-slot:cell(action)="row">
                <b-button title="Delete API key" variant="outline-danger" @click="deleteApiKey(row.item.id)">
                    <b-icon-trash style="width: 20px; height: 20px"></b-icon-trash>
                </b-button>
            </template>
        </b-table>
        <DeleteApiKey :apiKeyId="apiKeyIdToDelete" @cleanup-api-key-id-to-delete="apiKeyIdToDelete = undefined"
            @list-api-keys="$emit('list-api-keys')" />
    </div>
</template>

<script>
import DeleteApiKey from "./DeleteApiKey"

export default {
    props: ["apiKeys"],
    components: {
        DeleteApiKey
    },
    data() {
        return {
            apiKeyIdToDelete: undefined,
            fields: [
                {
                    key: "id",
                    label: "ID",
                },
                {
                    key: "key",
                    label: "API key",
                },
                {
                    key: "action",
                    label: "Action",
                    class: "text-right",
                },
            ],
        }
    },
    methods: {
        deleteApiKey(keyId) {
            this.apiKeyIdToDelete = keyId
            this.$bvModal.show("delete-api-key-modal")
        }
    },
}
</script>

<style>

</style>
