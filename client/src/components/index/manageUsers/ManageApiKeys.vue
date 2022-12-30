<template>
    <b-modal ref="manageApiKeysModal" id="manage-api-keys-modal" :title="`API keys for user ${user.username}`"
        @show="listApiKeys()" @hidden="$emit('cleanup'); apiKeys = []" hide-footer>
        <ApiKeysTable :apiKeys="apiKeys" @list-api-keys="listApiKeys()" />
    </b-modal>
</template>

<script>
import axios from "axios"

import ApiKeysTable from '../security/ApiKeysTable'

const basePath = "/api"

export default {
    props: ["user"],
    components: {
        ApiKeysTable
    },
    data() {
        return {
            apiKeys: []
        }
    },
    methods: {
        listApiKeys() {
            const path = `${basePath}/user/${this.user.id}/apikey`

            axios
                .get(path)
                .then((response) => {
                    this.apiKeys = response.data
                })
                .catch((error) => {
                    this.handleError(error)
                })
        },
    },
};
</script>
<style>

</style>
