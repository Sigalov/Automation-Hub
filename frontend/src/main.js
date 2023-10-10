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

let socket = new WebSocket('ws://' + window.location.host + '/ws/console/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const blockId = data.blockId;
    const message = data.message;

    let consoleOutput = document.querySelector(`textarea[name="console_output_${blockId}"]`);
    consoleOutput.value += message + '\n';
};
// function updateConsoleOutput(blockId) {
//     fetch(`/get_console_output/${blockId}/`)
//         .then(response => response.json())
//         .then(data => {
//             const consoleElement = document.getElementById(`console_output_${blockId}`);
//             consoleElement.textContent = data.console_output;
//         });
// }
//
// // Periodically update the console output for each block every 5 seconds (or desired interval)
// setInterval(function() {
//     const blockIds = [...document.querySelectorAll('.console-output')].map(element => element.dataset.blockId);
//     blockIds.forEach(blockId => updateConsoleOutput(blockId));
// }, 5000);
function updateConsoleOutput() {
    // Get all blocks (by any means you identify them, e.g., a common class)
    const blocks = document.querySelectorAll('.console-output');

    blocks.forEach(block => {
        const blockId = block.id.split('_').pop();

        fetch(`/get_console_output/${blockId}/`)
            .then(response => response.text())
            .then(consoleOutput => {
                block.textContent = consoleOutput;
            });
    });
}

// Call the function every 5 seconds to update the console output
setInterval(updateConsoleOutput, 5000);
