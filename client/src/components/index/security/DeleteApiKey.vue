<template>
    <b-modal ref="deleteApiKeyModal" id="delete-api-key-modal" title="Are you sure?" hide-footer>
        <div class="text-right">
            <b-button @click="deleteApiKey(apiKeyId)" variant="outline-danger">Yes, delete this API key</b-button>
            <b-button class="ml-2" @click="$refs.deleteApiKeyModal.hide()" variant="outline-secondary">Cancel</b-button>
        </div>
    </b-modal>
</template>

<script>
import axios from "axios"

const basePath = "/api"

export default {
    props: ["apiKeyId"],
    methods: {
        deleteApiKey(keyId) {
            const path = `${basePath}/user/apikey/${keyId}`

            axios
                .delete(path)
                .then((response) => {
                    void (response)
                    this.$emit('cleanup-api-key-id-to-delete')
                    this.$emit('list-api-keys')
                    this.$refs.deleteApiKeyModal.hide()
                })
                .catch((error) => {
                    this.handleError(error)
                })
        },
    }
}
</script>
<style>

</style>
