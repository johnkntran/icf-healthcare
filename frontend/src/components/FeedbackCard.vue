<template>
  <div class="row">
    <div class="col s12">
      <div class="card cyan darken-1">
        <div class="card-content white-text">
          <span class="card-title">{{ feedback.title }}</span>
          <p>{{ feedback.body }}</p>
          <code class="grey-text text-lighten-1">Timestamp: {{ feedback.created.toISOString() }}</code>
          <div v-if="feedback.insight" class="orange-text text-lighten-4">
            <h5>AI Insight</h5>
            <p>{{ feedback.insight.summary }}</p>
            <table>
              <tbody>
                <tr>
                  <td>Sentiment</td>
                  <td>{{ feedback.insight.sentiment }}</td>
                </tr>
                <tr>
                  <td>Key Topics</td>
                  <td>{{ feedback.insight.keyTopics.join(', ') }}</td>
                </tr>
                <tr>
                  <td>Action Required</td>
                  <td>{{ feedback.insight.action_required }}</td>
                </tr>
                <tr>
                  <td>Latency</td>
                  <td>{{ feedback.insight.latency.toFixed(2) }} secs</td>
                </tr>
                <tr>
                  <td>Tokens Used</td>
                  <td>{{ feedback.insight.tokens }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-action">
          <a href="#" @click.prevent="saveInsight" v-if="!feedback.insight && !isThinking">
            Generate AI Insight for this Feedback
          </a>
          <span v-if="!feedback.insight && isThinking">
            Processing Insight... please wait
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import type { Feedback } from '../interfaces.ts';
  import { ref } from 'vue';

  const props = defineProps<{feedback: Feedback}>();
  const emit = defineEmits(['saved']);
  console.log(props.feedback.insight);
  const isThinking = ref(false);

  async function saveInsight(): Promise<undefined> {
    isThinking.value = true;
    try {
      const resp = await fetch(
        'http://localhost:8000/insight', 
        {
          method: 'POST', 
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            feedback_id: props.feedback.id,
          }),
        }
      );
    } catch {
      return M.toast({html: 'Something went wrong saving the feedback.', classes: 'red accent-3'});
    }
    isThinking.value = false;
    emit('saved');
  }
</script>