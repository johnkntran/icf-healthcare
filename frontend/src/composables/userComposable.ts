import { ref, onMounted } from 'vue';
import type { User, Feedback, Insight } from '../interfaces.ts';
import { useUserStore } from '../stores';

export function useUserComposable() {

  const store = useUserStore();

  const feedbacks = ref([]);

  async function userSaved(name: string): Promise<undefined> {
    store.setUsername(name);
    store.setUserWasSaved(true);
    await getFeedbackAndInsights();
  }

  async function getFeedbackAndInsights(): Promise<undefined> {
    const params = new URLSearchParams({username: store.username});
    try {
      const resp = await fetch(
        `http://localhost:8000/feedback_and_insights?${params}`, 
        {
          method: 'GET', 
          headers: {'Content-Type': 'application/json'},
        }
      );
      const data = await resp.json();
      const results = [];
      for (let d of data) {
        const user: User = {
          id: d.feedback.user.id, 
          username: d.feedback.user.username,
        }
        const insight: Insight | null = d.insight ? {
          sentiment: d.insight.sentiment,
          keyTopics: d.insight.key_topics,
          action_required: d.insight.action_required,
          summary: d.insight.summary,
          tokens: d.insight.tokens,
          latency: d.insight.latency,
        } : null;
        const feedback: Feedback = {
          id: d.feedback.id,
          user: user,
          title: d.feedback.title,
          body: d.feedback.body,
          created: new Date(d.feedback.created),
          updated: new Date(d.feedback.updated),
          insight: insight,
        };
        results.push(feedback);
      }
      feedbacks.value = results;
    } catch {
      return M.toast({html: 'Something went wrong fetching feedback and insight data!', classes: 'red accent-3'});
    }
  }

  onMounted(async () => {
    M.updateTextFields();
    if (store.username) {
      await getFeedbackAndInsights();
    }
  });

  return { feedbacks, userSaved, getFeedbackAndInsights };
}