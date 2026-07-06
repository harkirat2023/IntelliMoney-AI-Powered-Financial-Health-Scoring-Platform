import { useCallback, useEffect, useRef, useState } from "react";
import { copilotStore } from "../../store/copilotStore";
import { Send, Bot, User, Loader } from "lucide-react";

export default function CopilotChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const chatEnd = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    copilotStore.fetchSuggestions().then(() => {
      setSuggestions(copilotStore.suggestions);
    });
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
