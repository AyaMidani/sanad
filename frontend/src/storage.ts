import type { Conversation } from "./types";

const KEY = "sanad.conversations";

export function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Conversation[]) : [];
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(conversations));
  } catch {
    // Storage is full or blocked: history just won't be saved.
  }
}
