import { useState, useCallback } from 'react';
import { Message } from '@/types/chat';

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  return { messages, activeSessionId };
}
