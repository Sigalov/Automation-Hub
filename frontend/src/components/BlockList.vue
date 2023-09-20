<template>
    <div>
        <h1>Blocks</h1>
        <ul>
            <li v-for="block in blocks" :key="block.id">
                {{ block.block_id }} - {{ block.status }}
            </li>
        </ul>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            blocks: []
        };
    },
    mounted() {
        axios.get('http://localhost:8000/api/blocks/')
             .then(response => {
                 this.blocks = response.data;
             });
    }
}
</script>
