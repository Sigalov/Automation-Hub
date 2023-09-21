import { createApp, defineAsyncComponent } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';

const BlockList = defineAsyncComponent(() => import('./components/BlockList.vue'));

const routes = [
    // { path: '/', component: BlockList },
    { path: '/blocks', component: BlockList }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

createApp(App)
  .use(router)  // Use the router in your Vue app
  .mount('#app');
