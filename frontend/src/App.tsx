import { useEffect, useRef, useState, type FormEvent } from "react";
import Markdown from "react-markdown";
import Sidebar from "./components/Sidebar";
import { loadConversations, saveConversations } from "./storage";
import type { Conversation, Message } from "./types";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

const EXAMPLES = [
  "How much does it cost to replace a debit card?",
  "ما هي رسوم استبدال بطاقة الخصم؟",
  "What documents do I need for home finance?",
];

function App() {
  const [conversations, setConversations] =
    useState<Conversation[]>(loadConversations);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const active = conversations.find((c) => c.id === activeId);
  const messages = active?.messages ?? [];

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, loading]);

  function addMessage(id: string, message: Message) {
    setConversations((all) =>
      all.map((c) =>
        c.id === id ? { ...c, messages: [...c.messages, message] } : c
      )
    );
  }

  async function send(text: string) {
    const q = text.trim();
    if (!q || loading) return;

    let id = activeId;
    if (!id) {
      id = crypto.randomUUID();
      const conversation: Conversation = {
        id,
        title: q.slice(0, 60),
        createdAt: Date.now(),
        messages: [],
      };
      setConversations((all) => [conversation, ...all]);
      setActiveId(id);
    }
    const conversationId = id;

    addMessage(conversationId, { role: "user", text: q });
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string" ? data.detail : "Something went wrong."
        );
      }
      addMessage(conversationId, {
        role: "assistant",
        text: data.text,
        sources: data.sources,
      });
    } catch (err) {
      addMessage(conversationId, {
        role: "error",
        text: err instanceof Error ? err.message : "Something went wrong.",
      });
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    send(question);
  }

  function handleNew() {
    setActiveId(null);
    setSidebarOpen(false);
  }

  function handleSelect(id: string) {
    setActiveId(id);
    setSidebarOpen(false);
  }

  function handleDelete(id: string) {
    setConversations((all) => all.filter((c) => c.id !== id));
    if (id === activeId) setActiveId(null);
  }

  return (
    <div className="layout">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        open={sidebarOpen}
        onSelect={handleSelect}
        onNew={handleNew}
        onDelete={handleDelete}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="main">
        <header className="topbar">
          <button
            className="menu"
            aria-label="Open history"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>
          <span dir="auto">{active ? active.title : "New chat"}</span>
        </header>

        <main className="chat">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Ask about DIB cards and home finance</h2>
              <p>
                Answers come only from DIB's public documents, with the page
                they came from.
              </p>

              <div className="features">
                <div className="feature">
                  <span className="icon">✓</span>
                  <strong>Cited answers</strong>
                  <p>Every answer shows the PDF and page it came from.</p>
                </div>
                <div className="feature">
                  <span className="icon">ع</span>
                  <strong>Arabic & English</strong>
                  <p>Ask in either language.</p>
                </div>
                <div className="feature">
                  <span className="icon">§</span>
                  <strong>No guessing</strong>
                  <p>If the documents don't say it, Sanad says so.</p>
                </div>
              </div>

              <div className="examples">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    dir="auto"
                    className="example"
                    onClick={() => send(ex)}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`} dir="auto">
              {m.role === "assistant" ? (
                <>
                  <Markdown>{m.text}</Markdown>
                  {m.sources.length > 0 && (
                    <div className="sources" dir="ltr">
                      {m.sources.map((s) => (
                        <span key={s.number} className="chip">
                          [{s.number}] {s.file} · {s.title}
                        </span>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <p>{m.text}</p>
              )}
            </div>
          ))}

          {loading && (
            <div className="message assistant typing">
              Sanad is reading the documents…
            </div>
          )}
          <div ref={bottomRef} />
        </main>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            dir="auto"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask in English or Arabic…"
          />
          <button type="submit" disabled={loading || !question.trim()}>
            Ask
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
