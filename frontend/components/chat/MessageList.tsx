import React, { useEffect, useRef } from 'react';

export function useScrollToBottom() {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  });
  return endRef;
}
