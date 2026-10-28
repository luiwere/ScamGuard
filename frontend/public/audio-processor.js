/**
 * AudioWorkletProcessor for ScamGuard
 * Downsamples native microphone audio (44.1kHz / 48kHz) to 16,000Hz Mono PCM16.
 * Emits 250ms chunks (4000 samples = 8000 bytes) via zero-copy ArrayBuffer transfer.
 */
class ScamGuardAudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.targetSampleRate = 16000;
    // Chunk size: 250ms @ 16kHz = 4,000 samples
    this.chunkSize = 4000;
    this.buffer = new Float32Array(this.chunkSize * 2);
    this.bufferIndex = 0;
    this.lastRatio = sampleRate / this.targetSampleRate;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    // Mono channel (use channel 0)
    const channelData = input[0];
    const sourceSampleRate = sampleRate;
    const ratio = sourceSampleRate / this.targetSampleRate;

    // Resample channelData to 16kHz using linear interpolation
    for (let i = 0; i < channelData.length; i += ratio) {
      const index = Math.floor(i);
      const nextIndex = Math.min(index + 1, channelData.length - 1);
      const factor = i - index;
      const interpolated = (1 - factor) * channelData[index] + factor * channelData[nextIndex];

      this.buffer[this.bufferIndex++] = interpolated;

      // When we accumulate 250ms worth of 16kHz audio (4000 samples)
      if (this.bufferIndex >= this.chunkSize) {
        // Convert Float32 (-1.0 to 1.0) to PCM16 Int16 (-32768 to 32767)
        const pcm16 = new Int16Array(this.chunkSize);
        for (let j = 0; j < this.chunkSize; j++) {
          const s = Math.max(-1, Math.min(1, this.buffer[j]));
          pcm16[j] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Send binary buffer to main thread (zero-copy transfer)
        this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
        this.bufferIndex = 0;
      }
    }

    return true;
  }
}

registerProcessor('scamguard-audio-processor', ScamGuardAudioProcessor);
