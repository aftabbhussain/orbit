import { useState } from 'react';
import { Message } from '@/types/chat';

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  return { messages };
}
