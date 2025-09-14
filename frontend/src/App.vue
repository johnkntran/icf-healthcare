<template>
  <main>
    <nav>
      <div class="nav-wrapper cyan">
        <ul id="nav-mobile" class="left">
          <li><RouterLink to="/">Home</RouterLink></li>
          <li><RouterLink to="/analytics">Analytics</RouterLink></li>
        </ul>
      </div>
    </nav>
    <RouterView id="main-view" />
  </main>
</template>

<script setup lang="ts">
  import { RouterLink, RouterView } from 'vue-router';
  M.AutoInit();
</script>

<style scoped>
  main {
    margin: 1%;
  }
  #main-view {
    margin-top: 2%;
  }
</style>
