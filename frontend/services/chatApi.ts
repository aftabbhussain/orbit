// parse sse stream chunks into structured events
export interface StreamHandlers {
  onToken: (token: string) => void;
  onThought: (thought: any) => void;
  onCitation: (citation: any) => void;
  onDone: () => void;
}
