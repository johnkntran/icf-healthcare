<template>
  <section class="container">
    <UsernameForm @saved="userSaved"></UsernameForm>
    <article class="row">
      <div class="col s6">
        <FeedbackForm 
          :username="store.username" 
          @saved="feedbackSaved" 
          v-show="store.username">
        </FeedbackForm>
      </div>
      <div class="col s6">
        <ul>
          <li v-for="feedback in feedbacks" :key="feedback.id">
            <FeedbackCard 
              :feedback="feedback" 
              @saved="insightSaved">
            </FeedbackCard>
          </li>
        </ul>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
  import UsernameForm from '@/components/UsernameForm.vue';
  import FeedbackForm from '@/components/FeedbackForm.vue';
  import FeedbackCard from '@/components/FeedbackCard.vue';
  import { useUserComposable } from '@/composables/userComposable.ts';
  import { useUserStore } from '../stores';

  const store = useUserStore();

  const { feedbacks, userSaved, getFeedbackAndInsights } = useUserComposable();

  async function feedbackSaved(): Promise<undefined> {
    await getFeedbackAndInsights();
  }

  async function insightSaved(): Promise<undefined> {
    await getFeedbackAndInsights();
  }
</script>

<style scoped>
  .checkmark {
    margin: 2px;
    border-radius: 10px;
  }
</style>