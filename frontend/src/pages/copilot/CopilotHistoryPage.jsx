import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { copilotStore } from "../../store/copilotStore";
import { MessageSquare, Trash2, Clock, Loader } from "lucide-react";

export default function CopilotHistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    copilotStore.fetchSessions().then(() => {
      setSessions(copilotStore.sessions);
      setLoading(false);
    });
  }, []);

  const handleDeleteAll = async () => {
    if (!window.confirm("Delete all chat sessions?")) return;
    await copilotStore.deleteAll();
    setSessions([]);
  };

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="copilot-history-page">
      <div className="page-header">
        <h2><MessageSquare size={20} /> Chat History</h2>
        {sessions.length > 0 && (
          <button className="btn btn-outline btn-sm" onClick={handleDeleteAll}>
            <Trash2 size={16} /> Clear All
          </button>
        )}
      </div>
      {sessions.length === 0 ? (
        <div className="empty-state">
          <MessageSquare size={48} />
          <p>No chat sessions yet</p>
        </div>
      ) : (
        <div className="session-list">
          {sessions.map((s) => (
            <div key={s.id} className="session-card" onClick={() => navigate(`/app/copilot/history/${s.id}`)}>
              <div className="session-title">{s.title}</div>
              <div className="session-meta">
                <span><MessageSquare size={14} /> {s.message_count} messages</span>
                <span><Clock size={14} /> {new Date(s.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
