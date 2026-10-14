import React, { useState } from 'react';
import { Message } from '@/types/chat';

export function MessageBubble({ message }: { message: Message }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div>
      {message.thoughts && (
        <button onClick={() => setExpanded(!expanded)}>Thoughts ({message.thoughts.length})</button>
      )}
      <div>{message.content}</div>
    </div>
  );
}
