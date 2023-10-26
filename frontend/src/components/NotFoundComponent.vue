<!-- components/NotFoundComponent.vue -->

<template>
  <div class="not-found">
    <h1>404 Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <router-link to="/">Go back to the homepage</router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFoundComponent'
}
</script>

<style scoped>
.not-found {
  text-align: center;
  margin-top: 50px;
}
</style>
