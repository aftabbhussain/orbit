import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '@/types/chat';

export function MessageBubble({ message }: { message: Message }) {
  return (
    <div className="prose dark:prose-invert max-w-none">
      <ReactMarkdown>{message.content}</ReactMarkdown>
    </div>
  );
}
