// Audio Worklet Processor for capturing PCM audio
class RecorderProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferSize = 256;
  }
  
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input && input[0]) {
      this.port.postMessage({
        type: 'audio',
        data: input[0].slice()
      });
    }
    return true;
  }
}

registerProcessor('recorder-processor', RecorderProcessor);