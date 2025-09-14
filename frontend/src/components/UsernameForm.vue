<template>
  <div class="row">
    <form class="col s12">
      <div class="row">
        <div class="input-field col s5">
          <i class="material-icons prefix">account_circle</i>
          <input 
            id="username" 
            type="text" 
            class="validate" 
            v-model="store.username"
          >
          <label for="username">Username</label>
        </div>
        <div class="input-field col s2">
          <button 
            class="btn waves-effect waves-light pink" 
            type="submit" 
            name="submit-username" 
            @click.prevent="saveUser"
            :disabled="store.username == ''"
          >
            Save
          </button>
        </div>
        <div class="input-field col s5"></div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
  import type { User } from '../interfaces.ts';
  import { useUserStore } from '../stores';

  const store = useUserStore();

  const emit = defineEmits(['saved']);

  async function saveUser(): Promise<undefined> {
    try {
      const resp = await fetch(
        'http://localhost:8000/user', 
        {
          method: 'POST', 
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({username: store.username}),
        }
      );
      const user: User = await resp.json();
      M.toast({html: `${user.username} has been saved`, classes: 'green'});
      emit('saved', user.username);
    } catch {
      return M.toast({html: 'Something went wrong saving your username!', classes: 'red accent-3'});
    }
  }
</script>

<style scoped>
  .checkmark {
    margin: 2px;
    border-radius: 10px;
  }
</style>