import { useState, type FormEvent } from "react";
import "./App.css";

type Source = { number: number; file: string; title: string };
type Answer = { text: string; sources: Source[] };

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer(null);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string" ? data.detail : "Something went wrong."
        );
      }
      setAnswer(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>Sanad</h1>
      <p className="subtitle">Ask about DIB bank products, in Arabic or English.</p>

      <form onSubmit={handleSubmit}>
        <input
          dir="auto"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="How much does it cost to replace a debit card?"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {answer && (
        <section className="answer">
          <p dir="auto">{answer.text}</p>
          <h2>Sources</h2>
          <ul>
            {answer.sources.map((s) => (
              <li key={s.number}>
                [{s.number}] {s.file}, {s.title}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}

export default App;
