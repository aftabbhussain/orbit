export interface ThoughtStep {
  thought: string;
  action?: string | null;
  observation?: string | null;
}

export interface Citation {
  id: number;
  title: string;
  content: string;
  source?: string | null;
  score?: number | null;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  thoughts?: ThoughtStep[];
  citations?: Citation[];
}
