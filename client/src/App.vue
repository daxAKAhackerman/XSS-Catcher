<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.modal-backdrop:not(.show):not(.fade) {
  opacity: 0.5 !important;
}
</style>
