import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Banpick from '../views/Banpick.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/banpick', component: Banpick }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
