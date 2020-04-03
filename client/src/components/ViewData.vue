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

    <h1 class="text-left">Cookies</h1>

    <table class="table table-hover" style="table-layout: fixed; width: 100%">
      <tbody>
        <tr
          v-for="(cookie_value,cookie_id) in data.cookies"
          v-bind:key="cookie_id"
        >
          <td width="90%" class="text-left">
            <div v-for="(value, key) in cookie_value" v-bind:key="key">
              <code>{{ key }} => {{ value}}</code>
            </div>
          </td>
          <td class="text-right">
            <b-button
              v-if="owner_id === user_id || is_admin"
              v-b-tooltip.hover title="Delete data"
              @click="to_delete_type = 'cookies'; to_delete = cookie_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            ><b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
            </b-button>
          </td>
        </tr>

      </tbody>
    </table>

    <h1 class="text-left">Local storage</h1>

    <table class="table table-hover" style="table-layout: fixed; width: 100%">
      <tbody>
        <tr
          v-for="(local_storage_value,local_storage_id) in data.local_storage"
          v-bind:key="local_storage_id"
        >
          <td width="90%" class="text-left">
            <div v-for="(value, key) in local_storage_value" v-bind:key="key">
              <code>{{ key }} => {{ value}}</code>
            </div>
          </td>
          <td class="text-right">
            <b-button
              v-if="owner_id === user_id || is_admin"
              v-b-tooltip.hover title="Delete data"
              @click="to_delete_type = 'local_storage'; to_delete = local_storage_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            ><b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Session storage</h1>

    <table class="table table-hover" style="table-layout: fixed; width: 100%">
      <tbody>
        <tr
          v-for="(session_storage_value,session_storage_id) in data.session_storage"
          v-bind:key="session_storage_id"
        >
          <td width="90%" class="text-left">
            <div v-for="(value, key) in session_storage_value" v-bind:key="key">
              <code>{{ key }} => {{ value}}</code>
            </div>
          </td>
          <td class="text-right">
            <b-button
              v-if="owner_id === user_id || is_admin"
              v-b-tooltip.hover title="Delete data"
              @click="to_delete_type = 'session_storage'; to_delete = session_storage_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            ><b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <h1 class="text-left">Other data</h1>

    <table class="table table-hover" style="table-layout: fixed; width: 100%">
      <tbody>
        <tr
          v-for="(other_value,other_id) in data.other_data"
          v-bind:key="other_id"
        >
          <td width="90%" class="text-left">
            <div style="word-wrap: break-word" v-for="(value, key) in other_value" v-bind:key="key">
              <div v-if="key == 'screenshot'">
                <h4>Screenshot</h4>
                <p><img style="max-width:100%" :src=value /></p>
              </div>
              <div v-else-if="key == 'fingerprint'">
                <h4>Fingerprint</h4>
                <p><vue-json-pretty
                  :deep=0
                  :showLength=true
                  :data=value
                ></vue-json-pretty></p>
              </div>
              <div v-else-if="key == 'dom'">
                <h4>DOM</h4>
                <p>
                  <a href="#" v-b-toggle.collapse-1 variant="primary">[Click to view DOM...]</a>
                  <b-collapse id="collapse-1">
                    <div v-highlight >
                      <pre class="language-html"><code>{{ value }}</code></pre>
                    </div>
                  </b-collapse>
                </p>
              </div>
              <div v-else>
                <h4>Data</h4>
                <p><code>{{ key }} => {{ value}}</code></p>
              </div>
            </div>
          </td>
          <td class="text-right">
            <b-button
              v-if="owner_id === user_id || is_admin"
              v-b-tooltip.hover title="Delete data"
              @click="to_delete_type = 'other_data'; to_delete = other_id"
              v-b-modal.delete-data-modal
              type="button"
              variant="danger"
            ><b-icon-trash style="width: 20px; height: 20px;"></b-icon-trash>
            </b-button>
          </td>
        </tr>
      </tbody>
    </table>

    <b-modal
    ref="deleteDataModal"
    id="delete-data-modal"
    title="Are you sure?"
    hide-footer
    >
      <b-form
        @submit="deleteData"
        @reset="$refs.deleteDataModal.hide()"
      >

        <b-button
          type="submit"
          variant="danger"
        >Yes, delete this entry</b-button>
        <b-button type="reset">Cancel</b-button>

      </b-form>
    </b-modal>

  </b-modal>

</template>

<script>

import axios from 'axios'
import VueJsonPretty from 'vue-json-pretty'

axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded'

const basePath = '/api'

export default {
  props: ['client_id', 'is_admin', 'owner_id', 'user_id'],
  components: {
    VueJsonPretty
  },
  data () {
    return {
      data: {},
      to_delete: 0,
      to_delete_type: ''
    }
  },
  methods: {
    getData () {
      const path = basePath + '/client/' + this.client_id + '/loot'

      axios.get(path)
        .then(response => {
          this.data = response.data
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    deleteData () {
      const path = basePath + '/xss/' + this.to_delete + '/' + this.to_delete_type

      axios.delete(path)
        .then(response => {
          this.getData()
          this.$refs.deleteDataModal.hide()
        })
        .catch(error => {
          if (error.response.status === 401) { this.$router.push({ name: 'Login' }) } else {}
        })
    },
    cleanup () {
      this.data = {}
      this.to_delete = 0
      this.to_delete_type = ''
      this.$parent.getClients()
    }
  }

}

</script>

<style></style>
