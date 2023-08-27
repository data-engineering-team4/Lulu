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
