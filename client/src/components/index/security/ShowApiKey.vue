<template>
    <b-modal ref="showApiKeyModal" id="show-api-key-modal" title="API key created" hide-footer @hide="cleanup()">
        <p>API key: {{ apiKey }}</p>
        <div class="text-right">
            <b-button @click="cleanup()" variant="outline-secondary">Close</b-button>
        </div>
    </b-modal>
</template>
<script>
export default {
    props: ["apiKey"],
    methods: {
        cleanup() {
            this.$emit("list-api-keys")
            this.$emit("cleanup-new-api-key")
            this.$refs.showApiKeyModal.hide()
        },
    },
};
</script>

<style>

</style>
