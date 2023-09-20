import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import BlockList from './components/BlockList.vue';
import NotFoundComponent from "@/components/NotFoundComponent.vue";

// Define routes
const routes = [
  {
    path: '/blocks',
    name: 'BlockList',
    component: BlockList
  },
  { path: '/blocks', component: BlockList },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundComponent }, // make sure to create or import a NotFoundComponent
  {
    path: '/:pathMatch(.*)*', // This is a catch-all route
    name: 'NotFound',
    component: NotFoundComponent
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Create and mount the app
const app = createApp(App);
app.use(router);
app.mount('#app');
