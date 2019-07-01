import Vue from 'vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import App from './App.vue'
import './assets/js/jquery-2.2.3'
import './assets/js/bootstrap'
import './assets/css/bootstrap.css'

Vue.config.productionTip = false
Vue.use(ElementUI);

new Vue({
  render: h => h(App),
  data: {
    eventHub: new Vue()
  }
}).$mount('#app')
