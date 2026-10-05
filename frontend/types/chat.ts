export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export interface StreamEvent {
  type: 'token' | 'thought' | 'citation' | 'done';
  data: any;
}
