import { useEffect, useRef, useState } from "react";

export function useWebSocket(channel, onMessage) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("intellimoney_token");
    if (!token) return;

    function connect() {
      const apiBase = process.env.API_BASE_URL || "http://localhost:8080/api/v1";
      const wsBase = apiBase.replace(/^http/, "ws");
      const url = `${wsBase}/ws?token=${token}`;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };
      ws.onmessage = (event) => {
        if (onMessage) {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch {
            if (event.data === "pong") return;
            onMessage(event.data);
          }
        }
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [channel, onMessage]);

  return { connected };
}
