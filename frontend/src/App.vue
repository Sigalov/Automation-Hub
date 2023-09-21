<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <h1>Practitest Connector</h1>

    <!-- Navbar or Header -->
    <div>
      <a href="/">Home</a> |
      <router-link to="/blocks">Blocks</router-link> <!-- This is your existing link to blocks -->
    </div>

    <!-- Content Area -->
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
