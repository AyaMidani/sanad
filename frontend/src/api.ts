import type { Conversation, Message, Segment, Source } from "./types";

const API_URL = import.meta.env.VITE_API_URL;
const VISITOR_KEY = "sanad.visitorId";

let visitorId: string | null = null;

function getVisitorId(): string {
  if (visitorId) return visitorId;
  try {
    visitorId = localStorage.getItem(VISITOR_KEY);
    if (!visitorId) {
      visitorId = `v_${crypto.randomUUID()}`;
      localStorage.setItem(VISITOR_KEY, visitorId);
    }
  } catch {
    visitorId = `v_${crypto.randomUUID()}`;
  }
  return visitorId;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Visitor-Id": getVisitorId(),
    },
  });
  if (res.status === 204) return undefined as T;

  const data = await res.json();
  if (!res.ok) {
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Something went wrong."
    );
  }
  return data as T;
}

export type AskResult = {
  conversation_id: string;
  text: string;
  sources: Source[];
};

export function fetchConversations() {
  return request<Conversation[]>("/conversations");
}

export function fetchMessages(conversationId: string) {
  return request<Message[]>(`/conversations/${conversationId}/messages`);
}

export function deleteConversation(conversationId: string) {
  return request<void>(`/conversations/${conversationId}`, {
    method: "DELETE",
  });
}

export function askQuestion(
  question: string,
  conversationId: string | null,
  segment: Segment | null,
) {
  return request<AskResult>("/ask", {
    method: "POST",
    body: JSON.stringify({ question, conversation_id: conversationId, segment }),
  });
}
