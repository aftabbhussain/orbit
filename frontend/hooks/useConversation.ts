import { useState, useCallback } from 'react';

export function useConversation() {
  const [messages, setMessages] = useState([]);
  const clearMessages = useCallback(() => setMessages([]), []);
  return { messages, clearMessages };
}
