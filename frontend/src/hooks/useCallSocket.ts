import { useState, useRef, useCallback, useEffect } from 'react';
import {
  ServerEvent,
  TranscriptEvent,
  TacticItem,
  RiskEvent,
  AlertEvent,
  TrustedContact,
  StartCallMessage,
  StopCallMessage,
} from '../types';

export type SocketStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

interface UseCallSocketOptions {
  wsUrl?: string;
}

export function useCallSocket(options: UseCallSocketOptions = {}) {
  const wsUrl = options.wsUrl || (
    window.location.protocol === 'https:'
      ? `wss://${window.location.hostname}:8000/ws/call`
      : `ws://${window.location.hostname}:8000/ws/call`
  );

  const [status, setStatus] = useState<SocketStatus>('disconnected');
  const [transcripts, setTranscripts] = useState<TranscriptEvent[]>([]);
  const [tactics, setTactics] = useState<TacticItem[]>([]);
  const [risk, setRisk] = useState<RiskEvent>({ type: 'risk', score: 0, level: 'safe' });
  const [alert, setAlert] = useState<AlertEvent | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const clearAlert = useCallback(() => setAlert(null), []);
  const clearError = useCallback(() => setError(null), []);

  const sendAudioChunk = useCallback((chunk: ArrayBuffer) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(chunk);
    }
  }, []);

  const stopCall = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const stopMsg: StopCallMessage = { type: 'stop' };
      wsRef.current.send(JSON.stringify(stopMsg));
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  const startCall = useCallback((contact?: TrustedContact, scenario?: string | null) => {
    // Reset state for new call
    setTranscripts([]);
    setTactics([]);
    setRisk({ type: 'risk', score: 0, level: 'safe' });
    setAlert(null);
    setError(null);
    setStatus('connecting');

    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;
      socket.binaryType = 'arraybuffer';

      socket.onopen = () => {
        setStatus('connected');
        const startMsg: StartCallMessage = {
          type: 'start',
          contact: contact || {},
          scenario: scenario || null,
        };
        socket.send(JSON.stringify(startMsg));
      };

      socket.onmessage = (event) => {
        if (typeof event.data === 'string') {
          try {
            const data: ServerEvent = JSON.parse(event.data);
            switch (data.type) {
              case 'transcript':
                setTranscripts((prev) => [...prev, data]);
                break;
              case 'tactics':
                setTactics((prev) => {
                  const newItems = data.items.filter(
                    (newItem) => !prev.some((p) => p.name === newItem.name && p.evidence === newItem.evidence)
                  );
                  return [...prev, ...newItems];
                });
                break;
              case 'risk':
                setRisk(data);
                break;
              case 'alert':
                setAlert(data);
                break;
              case 'error':
                setError(data.message);
                break;
            }
          } catch (e) {
            console.error('Failed to parse incoming server message:', e);
          }
        }
      };

      socket.onerror = (evt) => {
        console.error('WebSocket error:', evt);
        setError('WebSocket connection error. Is the ScamGuard backend running on port 8000?');
        setStatus('error');
      };

      socket.onclose = () => {
        setStatus('disconnected');
      };
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err);
      setError(`Failed to connect to backend: ${errMsg}`);
      setStatus('error');
    }
  }, [wsUrl]);

  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    status,
    transcripts,
    tactics,
    risk,
    alert,
    error,
    startCall,
    stopCall,
    sendAudioChunk,
    clearAlert,
    clearError,
  };
}
