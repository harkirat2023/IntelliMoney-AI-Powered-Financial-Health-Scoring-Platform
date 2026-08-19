import { useCallback, useEffect, useRef, useState } from "react";
import { copilotStore } from "../../store/copilotStore";
import { Send, Bot, User, Loader, Check, X, ShieldAlert } from "lucide-react";

const KIND_LABELS = {
  set_income: "Set monthly income",
  create_expense: "Record expense",
  update_expense: "Update expense",
  delete_expense: "Delete expense",
  create_budget: "Create budget",
  update_budget: "Update budget",
  delete_budget: "Delete budget",
  create_goal: "Create goal",
  update_goal: "Update goal",
  delete_goal: "Delete goal",
  create_recurring: "Add recurring expense",
  update_recurring: "Update recurring expense",
  delete_recurring: "Delete recurring expense",
  create_subscription: "Add subscription",
  update_subscription: "Update subscription",
  delete_subscription: "Delete subscription",
  mark_notification_read: "Mark notification read",
  recalculate_health: "Recalculate health score",
  sync_account: "Sync account",
  import_aa_data: "Import AA data",
};

function formatActionLabel(action) {
  const label = KIND_LABELS[action.kind] || action.kind;
  if (action.summary && action.summary !== label) return `${label}: ${action.summary}`;
  return label;
}

function ProposedChangesCard({ proposal, onConfirm, onCancel, busy }) {
  if (!proposal) return null;
  const done = proposal.status === "executed" || proposal.status === "partially_failed" || proposal.status === "cancelled";
  return (
    <div className={`proposal-card status-${proposal.status}`}>
      <div className="proposal-header">
        <ShieldAlert size={16} />
        <strong>Proposed Changes</strong>
        <span className="proposal-status">{proposal.status.replace("_", " ")}</span>
      </div>
      {proposal.status === "pending" && (
        <p className="proposal-hint">These changes will be applied only after you confirm. Nothing is saved yet.</p>
      )}
      <ul className="proposal-actions">
        {(proposal.actions || []).map((action, i) => (
          <li key={i} className={action.destructive ? "destructive" : ""}>
            {action.destructive && <X size={12} />}
            <span>{formatActionLabel(action)}</span>
          </li>
        ))}
      </ul>
      {proposal.status === "pending" && (
        <div className="proposal-buttons">
          <button className="btn-confirm" onClick={onConfirm} disabled={busy}>
            {busy ? <Loader size={14} className="spin" /> : <Check size={14} />} Confirm
          </button>
          <button className="btn-cancel" onClick={onCancel} disabled={busy}>
            <X size={14} /> Cancel
          </button>
        </div>
      )}
      {proposal.status === "executed" && <p className="proposal-result ok">All changes applied.</p>}
      {proposal.status === "partially_failed" && <p className="proposal-result warn">Some changes failed — review the execution report.</p>}
      {proposal.status === "cancelled" && <p className="proposal-result">Proposal cancelled. No changes were applied.</p>}
    </div>
  );
}

export default function CopilotChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [proposal, setProposal] = useState(null);
  const [proposalBusy, setProposalBusy] = useState(false);
  const chatEnd = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    copilotStore.fetchSuggestions().then(() => {
      setSuggestions(copilotStore.suggestions);
    });
    const unsub = copilotStore.subscribe((s) => setProposal(s.pendingProposal));
    return unsub;
  }, []);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || loading) return;
    setShowSuggestions(false);
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await copilotStore.sendMessage(text, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.message, id: res.message_id }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  }, [loading, sessionId]);

  const handleConfirm = useCallback(async () => {
    if (!proposal || proposal.status !== "pending") return;
    setProposalBusy(true);
    try {
      const updated = await copilotStore.confirmProposal(proposal.id);
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: updated.status === "executed"
          ? "Your changes were applied successfully."
          : `Your changes were partially applied (${updated.status.replace("_", " ")}).`,
      }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I could not apply the changes. Please try again." }]);
    } finally {
      setProposalBusy(false);
    }
  }, [proposal]);

  const handleCancel = useCallback(async () => {
    if (!proposal || proposal.status !== "pending") return;
    setProposalBusy(true);
    try {
      await copilotStore.cancelProposal(proposal.id);
      setMessages((prev) => [...prev, { role: "assistant", content: "The proposed changes were cancelled. Nothing was applied." }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I could not cancel the proposal. Please try again." }]);
    } finally {
      setProposalBusy(false);
    }
  }, [proposal]);

  const handleSuggestion = (text) => sendMessage(text);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="copilot-chat-container">
      <div className="copilot-messages">
        {messages.length === 0 && (
          <div className="copilot-welcome">
            <Bot size={48} />
            <h2>AI Copilot</h2>
            <p>Ask me anything about your finances</p>
            {showSuggestions && suggestions.length > 0 && (
              <div className="copilot-suggestions">
                {suggestions.map((s, i) => (
                  <button key={i} className="suggestion-chip" onClick={() => handleSuggestion(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`copilot-message ${msg.role}`}>
            <div className="msg-avatar">
              {msg.role === "user" ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className="msg-content">{msg.content}</div>
          </div>
        ))}
        {proposal && (
          <div className="copilot-message assistant">
            <div className="msg-avatar"><Bot size={18} /></div>
            <div className="msg-content">
              <ProposedChangesCard
                proposal={proposal}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
                busy={proposalBusy}
              />
            </div>
          </div>
        )}
        {loading && (
          <div className="copilot-message assistant">
            <div className="msg-avatar"><Bot size={18} /></div>
            <div className="msg-content typing"><Loader size={16} className="spin" /> Thinking...</div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>
      <div className="copilot-input-bar">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a financial question..."
          rows={1}
          disabled={loading}
        />
        <button className="btn-icon" onClick={() => sendMessage(input)} disabled={loading || !input.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
