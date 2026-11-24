'use client';

import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '@/types/chat';
import { MessageBubble } from './MessageBubble';

interface ConversationViewProps {
  messages: ChatMessage[];
}

export function ConversationView({ messages }: ConversationViewProps) {
  const scrollMarkerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollMarkerRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="text-center max-w-2xl mx-auto">
          <h1 className="text-3xl font-semibold text-gray-800 mb-4">
            arXiv Research Assistant
          </h1>
          <p className="text-gray-500 mb-8">
            Need help navigating AI and ML research? Ask me anything! I can find, summarize, and break down complex papers from arXiv for you.
          </p>
          <div className="grid gap-3 max-w-lg mx-auto">
            <StarterPrompt text="Find papers about transformer models" />
            <StarterPrompt text="What are the latest advances in LLMs?" />
            <StarterPrompt text="Summarize the paper about attention mechanisms" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-white">
      {messages.map((item) => (
        <MessageBubble key={item.id} message={item} />
      ))}
      <div ref={scrollMarkerRef} />
    </div>
  );
}

export const MessageList = ConversationView;

function StarterPrompt({ text }: { text: string }) {
  return (
    <button
      className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 text-left shadow-sm hover:shadow"
      onClick={() => {
        const customEvt = new CustomEvent('setInput', { detail: text });
        window.dispatchEvent(customEvt);
      }}
    >
      {text}
    </button>
  );
}
