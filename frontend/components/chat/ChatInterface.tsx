import React from 'react';
import { ConversationView } from './ConversationView';
import { MessageComposer } from './MessageComposer';

export function ChatInterface() {
  return (
    <div className="h-screen flex flex-col">
      <ConversationView />
      <MessageComposer />
    </div>
  );
}
