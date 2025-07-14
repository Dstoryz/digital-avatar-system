import { useState, useEffect, useRef, useCallback } from "react";
/// <reference types="node" />

type ConnectionStatus = "Connecting" | "Connected" | "Disconnected" | "Error";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = (
  url: string,
  options: Partial<UseWebSocketOptions> = {},
) => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("Disconnected");
  const [lastMessage, setLastMessage] = useState<string>("");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus("Connecting");

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus("Connected");
        setReconnectAttempts(0);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        setLastMessage(event.data);
        onMessage?.(event.data);
      };

      ws.onclose = (event) => {
        setConnectionStatus("Disconnected");
        onClose?.();

        // Попытка переподключения
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          setReconnectAttempts(reconnectAttemptsRef.current);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          setConnectionStatus("Error");
        }
      };

      ws.onerror = (error) => {
        setConnectionStatus("Error");
        onError?.(error);
      };
    } catch (error) {
      setConnectionStatus("Error");
      console.error("WebSocket connection error:", error);
    }
  }, [
    url,
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval,
    maxReconnectAttempts,
  ]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionStatus("Disconnected");
    setReconnectAttempts(0);
    reconnectAttemptsRef.current = 0;
  }, []);

  const sendMessage = useCallback((message: string | object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const messageString =
        typeof message === "string" ? message : JSON.stringify(message);
      wsRef.current.send(messageString);
      return true;
    }
    return false;
  }, []);

  // Автоматическое подключение при монтировании
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Очистка при размонтировании
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connectionStatus,
    lastMessage,
    reconnectAttempts,
    sendMessage,
    connect,
    disconnect,
  };
};
