import React from 'react';
import { Message } from '@/types/chat';

export function MessageItem({ message }: { message: Message }) {
  return <div>{message.content}</div>;
}

export function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div>
      {messages.map(m => <MessageItem key={m.id} message={m} />)}
    </div>
  );
}
