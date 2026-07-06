import { useEffect, useRef, useState } from "react";

export function useWebSocket(channel, onMessage) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("intellimoney_token");
    if (!token) return;

    function connect() {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = process.env.VITE_WS_HOST || window.location.host;
      const url = `${protocol}//${host}/api/v1/ws?token=${token}`;

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
