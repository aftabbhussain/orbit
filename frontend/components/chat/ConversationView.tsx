import React from 'react';

export function ConversationView({ onClear }: { onClear?: () => void }) {
  return (
    <div className="flex flex-col h-full">
      <header className="p-4 border-b flex justify-between">
        <h2>Academic Research Assistant</h2>
        <button onClick={onClear}>Clear</button>
      </header>
    </div>
  );
}
