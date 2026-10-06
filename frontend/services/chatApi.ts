import { ChatRequest, ChatResponse, PaperSource } from '@/types/chat';

const SERVER_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

export interface SessionHistoryResult {
  session_id: string;
  messages: Array<{
    role: string;
    content: string;
  }>;
}

export async function postChatMessage(data: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${SERVER_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: data.message,
      session_id: data.session_id,
    }),
  });

  if (!res.ok) {
    const errorDetails = await res.json().catch(() => null);
    throw new Error(
      errorDetails?.detail || `Server responded with HTTP ${res.status}`
    );
  }

  const dataObj = await res.json();

  const formattedSources: PaperSource[] = (dataObj.sources || []).map(
    (item: any, idx: number) => {
      const meta = item.metadata || {};
      const paperCode = item.arxiv_id ?? meta.arxiv_id ?? meta.paper_id;

      return {
        id: item.id ?? idx,
        title: item.title || meta.title || 'Untitled',
        score: typeof item.score === 'number' ? item.score : 0,
        year: item.year ?? meta.year,
        arxiv_id: paperCode,
        paper_id: item.paper_id ?? meta.paper_id,
        section: item.section ?? meta.section,
        categories: Array.isArray(item.categories)
          ? item.categories
          : Array.isArray(meta.categories)
          ? meta.categories
          : [],
        authors: Array.isArray(item.authors)
          ? item.authors
          : Array.isArray(meta.authors)
          ? meta.authors
          : [],
        pdf_url:
          item.pdf_url ??
          meta.pdf_url ??
          (paperCode ? `https://arxiv.org/pdf/${paperCode}.pdf` : undefined),
      };
    }
  );

  return {
    answer: dataObj.answer || '',
    session_id: dataObj.session_id || data.session_id || '',
    reasoning_steps: dataObj.reasoning_steps || [],
    sources: formattedSources,
    execution_time: dataObj.execution_time || 0,
    total_tokens: dataObj.total_tokens || 0,
  };
}

export const sendMessage = postChatMessage;

export async function fetchConversationHistory(
  sessionId: string
): Promise<SessionHistoryResult> {
  try {
    const res = await fetch(`${SERVER_BASE}/api/chat/history/${sessionId}`);
    if (!res.ok) {
      return { session_id: sessionId, messages: [] };
    }
    return await res.json();
  } catch {
    return { session_id: sessionId, messages: [] };
  }
}

export const getSessionHistory = fetchConversationHistory;

export async function purgeConversation(sessionId: string): Promise<void> {
  try {
    await fetch(`${SERVER_BASE}/api/chat/session/${sessionId}`, {
      method: 'DELETE',
    });
  } catch {
    // Non-critical cleanup
  }
}

export const clearSession = purgeConversation;
