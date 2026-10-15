import React from 'react';
import { Message } from '@/types/chat';

export function MessageBubble({ message }: { message: Message }) {
  return (
    <div>
      <div>{message.content}</div>
      {message.citations && (
        <div className="flex gap-2 mt-2">
          {message.citations.map(c => (
            <span key={c.id} className="badge">[{c.id}] {c.title}</span>
          ))}
        </div>
      )}
    </div>
  );
}
