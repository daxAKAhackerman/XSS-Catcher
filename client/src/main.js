import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Vue from 'vue'
import App from './App'
import router from './router'
import { BootstrapVue, IconsPlugin, BIcon, BIconArrowRepeat, BIconChevronDoubleUp, BIconChevronDoubleDown, BIconTrash, BIconInfo, BIconGear } from 'bootstrap-vue'
import Vue2Filters from 'vue2-filters'
import VueMoment from 'vue-moment'
import moment from 'moment-timezone'
import VueCodeHighlight from 'vue-code-highlight'
import VueClipboard from 'vue-clipboard2'

Vue.config.productionTip = false
VueClipboard.config.autoSetContainer = true

Vue.use(VueClipboard)
Vue.use(VueMoment, { moment })
Vue.use(Vue2Filters)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(VueCodeHighlight)
Vue.component('BIcon', BIcon)
Vue.component('BIconArrowRepeat', BIconArrowRepeat)
Vue.component('BIconChevronDoubleUp', BIconChevronDoubleUp)
Vue.component('BIconChevronDoubleDown', BIconChevronDoubleDown)
Vue.component('BIconTrash', BIconTrash)
Vue.component('BIconInfo', BIconInfo)
Vue.component('BIconGear', BIconGear)

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
