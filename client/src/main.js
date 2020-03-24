// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Vue from 'vue'
import App from './App'
import router from './router'
import { BootstrapVue, IconsPlugin, BIcon, BIconArrowRepeat, BIconChevronDoubleUp, BIconChevronDoubleDown, BIconTrash } from 'bootstrap-vue'
import Vue2Filters from 'vue2-filters'
import VueMoment from 'vue-moment'
import moment from 'moment-timezone'

Vue.use(VueMoment, { moment })
Vue.use(Vue2Filters)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.config.productionTip = false
Vue.component('BIcon', BIcon)
Vue.component('BIconArrowRepeat', BIconArrowRepeat)
Vue.component('BIconChevronDoubleUp', BIconChevronDoubleUp)
Vue.component('BIconChevronDoubleDown', BIconChevronDoubleDown)
Vue.component('BIconTrash', BIconTrash)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
