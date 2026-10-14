import React from 'react';
import { Message } from '@/types/chat';

export function MessageBubble({ message }: { message: Message }) {
  return <div className="p-4">{message.content}</div>;
}
