import { useState, useCallback } from 'react';
import { Message } from '@/types/chat';
import { streamChat } from '@/services/chatApi';

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  return { messages, isLoading };
}
