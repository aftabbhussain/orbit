import { useState, useCallback, useRef } from 'react';

export function useConversation() {
  const isSubmitting = useRef(false);
  return { isSubmitting };
}
