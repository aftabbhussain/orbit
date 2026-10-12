import { useState, useCallback } from 'react';
import { Message } from '@/types/chat';

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  const sendMessage = useCallback((text: string) => {
    const userMsg: Message = { id: Date.now().toString(), sender: 'user', content: text, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
  }, []);
  return { messages, sendMessage };
}
