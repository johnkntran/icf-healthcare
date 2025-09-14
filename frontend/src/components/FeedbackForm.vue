<template>
  <div class="row">
    <h3>Feedback Form</h3>
    <form class="col s12">
      <div class="row">
        <div class="input-field col s12">
          <input 
            id="title" 
            type="text" 
            class="validate" 
            v-model="title"
          >
          <label for="title">Title</label>
        </div>
      </div>
      <div class="row">
        <div class="input-field col s12">
          <textarea 
            id="body" 
            type="text" 
            class="materialize-textarea"
            v-model="body"
          ></textarea>
          <label for="body">Body</label>
        </div>
      </div>
      <div class="row">
        <div class="input-field col s12">
          <button 
            class="btn waves-effect waves-light pink" 
            type="submit" 
            name="submit-username" 
            @click.prevent="saveFeedback"
            :disabled="!title || !body"
          >
            Submit
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';

  const props = defineProps(['username']);
  const emit = defineEmits(['saved']);

  const title = ref('');
  const body = ref('');

  async function saveFeedback(): Promise<undefined> {
    try {
      const resp = await fetch(
        'http://localhost:8000/feedback', 
        {
          method: 'POST', 
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            username: props.username, 
            title: title.value,
            body: body.value,
          }),
        }
      );
    } catch {
      return M.toast({html: 'Something went wrong saving the feedback. Did you save your username first?', classes: 'red accent-3'});
    }
    title.value = '';
    body.value = '';
    emit('saved');
  }
</script>