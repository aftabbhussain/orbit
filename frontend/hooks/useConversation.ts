import { useState, useCallback } from 'react';
import { Message, Citation, ThoughtStep } from '@/types/chat';

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  return { messages };
}
