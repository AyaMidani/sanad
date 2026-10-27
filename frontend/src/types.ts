export type Source = { number: number; file: string; title: string };

export type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; text: string; sources: Source[] }
  | { role: "error"; text: string };

export type Conversation = {
  id: string;
  title: string;
  created_at: string;
};

export type Segment = "standard" | "wajaha" | "aayan" | "business";
