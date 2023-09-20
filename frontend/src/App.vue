<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <h1>Practitest Connector</h1>
    <BlockList />
  </div>
</template>

<script>
import BlockList from './BlockList.vue'; // Assuming BlockList.vue is in the same directory

export default {
  name: 'App',
  components: {
    BlockList
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
