import React, { useState, useRef } from 'react';

export function MessageComposer() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  return <textarea ref={textareaRef} rows={1} />;
}
