export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: PaperSource[];
  isStreaming?: boolean;
  isError?: boolean;
  timestamp: Date;
}

export type Message = ChatMessage;

export interface PaperSource {
  id: number;
  title: string;
  score: number;
  year?: number;
  arxiv_id?: string;
  paper_id?: string;
  section?: string;
  categories: string[];
  authors: string[];
  pdf_url?: string;
}

export type Source = PaperSource;

export interface MessagePayload {
  message: string;
  session_id?: string;
  stream?: boolean;
}

export type ChatRequest = MessagePayload;

export interface AssistantResponse {
  answer: string;
  session_id: string;
  reasoning_steps: ExecutionStep[];
  sources: PaperSource[];
  execution_time: number;
  total_tokens: number;
}

export type ChatResponse = AssistantResponse;

export interface ExecutionStep {
  thought: string;
  action?: string;
  action_input?: Record<string, unknown>;
  observation?: string;
}

export type ReasoningStep = ExecutionStep;

export interface StreamToken {
  type: 'token' | 'sources' | 'done' | 'error';
  data: string | Record<string, unknown>;
}

export type StreamChunk = StreamToken;
