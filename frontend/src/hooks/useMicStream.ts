import { useState, useRef, useCallback } from 'react';

interface UseMicStreamProps {
  onAudioChunk: (chunk: ArrayBuffer) => void;
}

export function useMicStream({ onAudioChunk }: UseMicStreamProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioLevel, setAudioLevel] = useState<number>(0);

  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;
    const buffer = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(buffer);
    let sum = 0;
    for (let i = 0; i < buffer.length; i++) {
      sum += buffer[i];
    }
    const average = sum / buffer.length;
    setAudioLevel(Math.min(100, Math.round((average / 128) * 100)));

    animFrameRef.current = requestAnimationFrame(updateAudioLevel);
  }, []);

  const stopMic = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }

    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  const startMic = useCallback(async () => {
    setError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access is not supported in this browser.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioContext = new AudioCtx();
      audioContextRef.current = audioContext;

      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      // Load AudioWorklet downsampler processor
      await audioContext.audioWorklet.addModule('/audio-processor.js');

      const sourceNode = audioContext.createMediaStreamSource(stream);
      const workletNode = new AudioWorkletNode(audioContext, 'scamguard-audio-processor');
      workletNodeRef.current = workletNode;

      // Handle downsampled 16kHz PCM16 chunks from the worklet thread
      workletNode.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
        onAudioChunk(event.data);
      };

      // Set up simple analyser for volume visualizer
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      sourceNode.connect(analyser);
      sourceNode.connect(workletNode);
      // Note: do not connect workletNode to destination to prevent mic feedback through speakers

      setIsRecording(true);
      updateAudioLevel();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(`Microphone error: ${msg}`);
      stopMic();
    }
  }, [onAudioChunk, stopMic, updateAudioLevel]);

  return {
    isRecording,
    audioLevel,
    error,
    startMic,
    stopMic,
  };
}
