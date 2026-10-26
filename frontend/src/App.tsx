import { useEffect, useRef, useState, type FormEvent } from "react";
import Markdown from "react-markdown";
import Sidebar from "./components/Sidebar";
import {
  askQuestion,
  deleteConversation,
  fetchConversations,
  fetchMessages,
} from "./api";
import type { Conversation, Message } from "./types";
import "./App.css";

const EXAMPLES = [
  "How much does it cost to replace a debit card?",
  "ما هي رسوم استبدال بطاقة الخصم؟",
  "What documents do I need for home finance?",
];

function errorText(err: unknown) {
  return err instanceof Error ? err.message : "Something went wrong.";
}

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const active = conversations.find((c) => c.id === activeId);

  useEffect(() => {
    fetchConversations()
      .then(setConversations)
      .catch(() => setConversations([]));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, loading]);

  async function send(text: string) {
    const q = text.trim();
    if (!q || loading) return;

    setMessages((m) => [...m, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);

    try {
      const result = await askQuestion(q, activeId);

      if (!activeId) {
        setActiveId(result.conversation_id);
        setConversations((all) => [
          {
            id: result.conversation_id,
            title: q.slice(0, 60),
            created_at: new Date().toISOString(),
          },
          ...all,
        ]);
      }

      setMessages((m) => [
        ...m,
        { role: "assistant", text: result.text, sources: result.sources },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", text: errorText(err) }]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    send(question);
  }

  function handleNew() {
    if (loading) return;
    setActiveId(null);
    setMessages([]);
    setSidebarOpen(false);
  }

  async function handleSelect(id: string) {
    if (loading) return;
    setActiveId(id);
    setMessages([]);
    setSidebarOpen(false);
    try {
      setMessages(await fetchMessages(id));
    } catch (err) {
      setMessages([{ role: "error", text: errorText(err) }]);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteConversation(id);
      setConversations((all) => all.filter((c) => c.id !== id));
      if (id === activeId) {
        setActiveId(null);
        setMessages([]);
      }
    } catch {
      // Delete failed: keep the chat in the list.
    }
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
          {!activeId && messages.length === 0 && (
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
                  {m.sources && m.sources.length > 0 && (
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
