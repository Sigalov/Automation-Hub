<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <h1>Practitest Connector</h1>
    <router-link to="/blocks">Blocks</router-link> <!-- Add this line for navigation -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
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
