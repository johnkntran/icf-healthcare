<template>
  <section>
    <h3>{{ props.title }}</h3>
    <canvas :id="props.chartId"></canvas>
  </section>
</template>

<script setup lang="ts">
  import { computed, onMounted } from 'vue'
  import type { Feedback, Insight } from '../interfaces.ts';

  const props = defineProps<{feedbacks: Feedback[], chartId: string, title: string}>();

  const insights = computed(() => {
    return props.feedbacks.filter(f => f.insight).map(f => f.insight);
  });

  onMounted(() => {
    const ctx = document.getElementById(props.chartId);
    new Chart(ctx, {
    type: 'line',
    data: {
      labels: [].concat(...Array(insights.value.length).fill(['Blue'])),
      datasets: [{
        label: props.chartId === 'token-chart' ? 'LLM Tokens (#)' : 'Latency (secs)',
        data: insights.value.map((i: Insight) => i[props.chartId === 'token-chart' ? 'tokens' : 'latency']),
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
});
</script>
