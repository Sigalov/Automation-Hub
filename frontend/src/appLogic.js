let socket = new WebSocket('ws://' + window.location.host + '/ws/console/');

socket.onopen = function(event) {
    console.log('WebSocket connection opened:', event);
};

socket.onerror = function(errorEvent) {
    console.error('WebSocket error:', errorEvent);
};

socket.onmessage = function(event) {
    console.log("WebSocket message received:", event.data);
    const data = JSON.parse(event.data);
    const blockId = data.blockId;
    let message = data.message;

    message = message.replace(/\\n/g, '\n');

    let consoleOutput = document.querySelector(`textarea[name="console_output_${blockId}"]`);
    consoleOutput.value = message + '\n' + consoleOutput.value;
};

function updateConsoleOutput() {
    const blocks = document.querySelectorAll('.console-output');

    blocks.forEach(block => {
        const blockId = block.id.split('_').pop();

        fetch(`/get_console_output/${blockId}/`)
            .then(response => response.json())
            .then(logEntries => {
                block.value = logEntries.join('\n');
            });
    });
}

setInterval(updateConsoleOutput, 5000);
