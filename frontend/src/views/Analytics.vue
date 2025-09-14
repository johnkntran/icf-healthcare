<template>
  <section class="container">
    <UsernameForm @saved="userSaved"></UsernameForm>
    <article v-if="feedbacks.length">
      <Chart title="LLM Tokens Used" chart-id="token-chart" :feedbacks="feedbacks"></Chart>
      <Chart title="Response Time (secs)" chart-id="latency-chart" :feedbacks="feedbacks"></Chart>
    </article>
  </section>
</template>

<script setup lang="ts">
  import UsernameForm from '@/components/UsernameForm.vue';
  import Chart from '@/components/Chart.vue';
  import { useUserComposable } from '@/composables/userComposable.ts';

  const { feedbacks, userSaved } = useUserComposable();
</script>
