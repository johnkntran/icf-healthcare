export interface User {
  id: string;
  username: string;
}

export interface Insight {
  sentiment: 'positive' | 'neutral' | 'negative';
  keyTopics: string[];
  action_required: boolean;
  summary: string;
  tokens: number;
  latency: number;
}

export interface Feedback {
  id: string;
  user: User;
  title: string;
  body: string;
  created: Date;
  updated: Date;
  insight: Insight | null;
}