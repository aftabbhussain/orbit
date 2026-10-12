'use client';

import { useState, useCallback, useRef } from 'react';
import { v4 as generateId } from 'uuid';
import { ChatMessage, PaperSource } from '@/types/chat';
import {
  postChatMessage,
  fetchConversationHistory,
  purgeConversation,
} from '@/services/chatApi';

const TICK_RATE_MS = 3;

interface ChatHookOptions {
  sessionId?: string;
  onError?: (err: Error) => void;
}

interface ChatHookState {
  messages: ChatMessage[];
  input: string;
  setInput: (txt: string) => void;
  isLoading: boolean;
  isStreaming: boolean;
  sessionId: string;
  sendMessage: () => Promise<void>;
  stopStreaming: () => void;
  clearMessages: () => void;
  loadSessionHistory: (sid: string) => Promise<void>;
}

export function useConversation(options: ChatHookOptions = {}): ChatHookState {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string>(
    options.sessionId || generateId()
  );

  const abortHandle = useRef<AbortController | null>(null);
  const timerHandle = useRef<NodeJS.Timeout | null>(null);

  const haltStreaming = useCallback(() => {
    if (timerHandle.current) {
      clearTimeout(timerHandle.current);
      timerHandle.current = null;
    }
    if (abortHandle.current) {
      abortHandle.current.abort();
      abortHandle.current = null;
    }
    setIsStreaming(false);
    setIsLoading(false);
  }, []);

  const appendMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const modifyMessage = useCallback(
    (id: string, updates: Partial<ChatMessage>) => {
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, ...updates } : m))
      );
    },
    []
  );

  const playStreamingAnimation = (
    text: string,
    assistantMsgId: string,
    sources: PaperSource[]
  ) => {
    setIsStreaming(true);
    let offset = 0;
    const characterList = text.split('');

    const tick = () => {
      if (offset >= characterList.length) {
        modifyMessage(assistantMsgId, {
          isStreaming: false,
          content: text,
          sources,
        });
        setIsStreaming(false);
        timerHandle.current = null;
        return;
      }

      const partialText = characterList.slice(0, offset + 1).join('');
      modifyMessage(assistantMsgId, {
        content: partialText,
        sources,
      });
      offset++;

      timerHandle.current = setTimeout(tick, TICK_RATE_MS);
    };

    timerHandle.current = setTimeout(tick, TICK_RATE_MS);
  };

  const handleSend = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userEntry: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    appendMessage(userEntry);
    setInput('');
    setIsLoading(true);

    const assistantEntryId = generateId();
    const assistantEntry: ChatMessage = {
      id: assistantEntryId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date(),
    };
    appendMessage(assistantEntry);

    abortHandle.current = new AbortController();

    try {
      const response = await postChatMessage({
        message: userEntry.content,
        session_id: sessionId,
      });

      playStreamingAnimation(
        response.answer,
        assistantEntryId,
        response.sources
      );

      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
      }
    } catch (err) {
      let failureNotice = 'An unexpected error occurred. Please try again.';

      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          failureNotice = 'Request was cancelled.';
        } else if (err.message.includes('Failed to fetch')) {
          failureNotice = 'Unable to reach backend service. Check network.';
        } else {
          failureNotice = err.message;
        }
      }

      modifyMessage(assistantEntryId, {
        content: `Error: ${failureNotice}`,
        isStreaming: false,
        isError: true,
      });

      options.onError?.(
        err instanceof Error ? err : new Error(failureNotice)
      );
      setIsStreaming(false);
    } finally {
      setIsLoading(false);
      abortHandle.current = null;
    }
  }, [input, isLoading, sessionId, appendMessage, modifyMessage, options]);

  const stopActiveStreaming = useCallback(() => {
    haltStreaming();

    setMessages((prev) => {
      const tail = prev[prev.length - 1];
      if (tail && tail.role === 'assistant') {
        return prev.map((m) =>
          m.id === tail.id ? { ...m, isStreaming: false } : m
        );
      }
      return prev;
    });
  }, [haltStreaming]);

  const resetChat = useCallback(async () => {
    haltStreaming();

    try {
      await purgeConversation(sessionId);
    } catch {
      // Ignored
    }

    setMessages([]);
    setSessionId(generateId());
    setInput('');
  }, [sessionId, haltStreaming]);

  const loadPastSession = useCallback(
    async (sid: string) => {
      setIsLoading(true);

      try {
        const historyData = await fetchConversationHistory(sid);
        const mappedEntries: ChatMessage[] = (
          historyData.messages || []
        ).map((item, idx) => ({
          id: `hist-${idx}`,
          role: item.role as 'user' | 'assistant',
          content: item.content,
          timestamp: new Date(),
        }));

        setMessages(mappedEntries);
        setSessionId(sid);
      } catch (err) {
        options.onError?.(
          err instanceof Error ? err : new Error('Failed to load history')
        );
      } finally {
        setIsLoading(false);
      }
    },
    [options]
  );

  return {
    messages,
    input,
    setInput,
    isLoading,
    isStreaming,
    sessionId,
    sendMessage: handleSend,
    stopStreaming: stopActiveStreaming,
    clearMessages: resetChat,
    loadSessionHistory: loadPastSession,
  };
}

export const useChat = useConversation;
