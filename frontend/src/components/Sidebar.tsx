import type { Conversation } from "../types";

type Props = {
  conversations: Conversation[];
  activeId: string | null;
  open: boolean;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onClose: () => void;
};

function groupLabel(timestamp: number): string {
  const startOfToday = new Date().setHours(0, 0, 0, 0);
  const day = 24 * 60 * 60 * 1000;
  if (timestamp >= startOfToday) return "Today";
  if (timestamp >= startOfToday - day) return "Yesterday";
  if (timestamp >= startOfToday - 7 * day) return "Previous 7 days";
  return "Older";
}

export default function Sidebar({
  conversations,
  activeId,
  open,
  onSelect,
  onNew,
  onDelete,
  onClose,
}: Props) {
  const groups: { label: string; items: Conversation[] }[] = [];
  for (const c of conversations) {
    const label = groupLabel(new Date(c.created_at).getTime());
    const last = groups[groups.length - 1];
    if (last && last.label === label) last.items.push(c);
    else groups.push({ label, items: [c] });
  }

  return (
    <>
      {open && <div className="backdrop" onClick={onClose} />}
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <div className="logo">س</div>
          <div>
            <strong>Sanad</strong>
            <span>DIB banking assistant</span>
          </div>
        </div>

        <button className="new-chat" onClick={onNew}>
          + New chat
        </button>

        <nav className="history">
          {conversations.length === 0 && (
            <p className="empty">Your conversations will appear here.</p>
          )}
          {groups.map((g) => (
            <div key={g.label} className="group">
              <h3>{g.label}</h3>
              {g.items.map((c) => (
                <div
                  key={c.id}
                  className={`item ${c.id === activeId ? "active" : ""}`}
                >
                  <button
                    className="item-title"
                    dir="auto"
                    onClick={() => onSelect(c.id)}
                  >
                    {c.title}
                  </button>
                  <button
                    className="item-delete"
                    aria-label="Delete conversation"
                    onClick={() => onDelete(c.id)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          ))}
        </nav>

        <footer className="sidebar-footer">
          Built by Aya Mydani ·{" "}
          <a
            href="https://github.com/AyaMidani/sanad"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
        </footer>
      </aside>
    </>
  );
}
