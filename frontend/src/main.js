import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './appLogic'; // import the logic file

createApp(App)
  .use(router)
  .mount('#app');
