import { createApp } from 'vue';
import App from './App.vue';
import store from './store';
import router from './router/router';
import axios from 'axios';

const app = createApp(App);
axios.defaults.baseURL = process.env.VUE_APP_BACKEND_API_URL || 'http://localhost:8000';

app.use(store);
app.use(router);

app.mount('#app');

app.directive('auto-font-size', (el, binding, vnode) => {
  // 엘리먼트가 페이지에 삽입될 때
  console.log(el, binding, vnode);
});



