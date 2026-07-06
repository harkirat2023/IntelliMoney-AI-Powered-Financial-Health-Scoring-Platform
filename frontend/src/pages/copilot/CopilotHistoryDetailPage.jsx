import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { copilotStore } from "../../store/copilotStore";
import { Bot, User, ArrowLeft, Loader } from "lucide-react";

export default function CopilotHistoryDetailPage() {
  const { sessionId } = useParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    copilotStore.fetchHistory(sessionId).then(() => {
      setMessages(copilotStore.messages);
      setLoading(false);
    });
  }, [sessionId]);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="copilot-history-detail">
      <button className="btn btn-ghost btn-sm" onClick={() => navigate("/app/copilot/history")}>
        <ArrowLeft size={16} /> Back
      </button>
      <div className="message-list">
        {messages.map((m, i) => (
          <div key={m.id || i} className={`copilot-message ${m.role}`}>
            <div className="msg-avatar">
              {m.role === "user" ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className="msg-content">{m.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
