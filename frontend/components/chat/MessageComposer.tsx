import React, { useState } from 'react';

export function MessageComposer({ onSend }: { onSend: (text: string) => void }) {
  const [input, setInput] = useState('');
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSend(input); setInput(''); }}>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button type="submit">Send</button>
    </form>
  );
}
