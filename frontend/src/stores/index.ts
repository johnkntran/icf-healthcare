import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUserStore = defineStore('userStore', () => {
  const username = ref('');
  const userWasSaved = ref(false);

  function setUsername(name: string) {
    username.value = name;
  }

  function setUserWasSaved(val: boolean) {
    userWasSaved.value = val;
  }

  return { username, userWasSaved, setUsername, setUserWasSaved };
});