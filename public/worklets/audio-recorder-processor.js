class AudioRecorderProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this.bufferSize = 4096
    this.buffer = new Float32Array(this.bufferSize)
    this.bufferIndex = 0
    this.isRecording = false
    
    this.port.onmessage = (event) => {
      if (event.data.type === 'START_RECORDING') {
        this.isRecording = true
        this.bufferIndex = 0
      } else if (event.data.type === 'STOP_RECORDING') {
        this.isRecording = false
        // Send any remaining buffered data
        if (this.bufferIndex > 0) {
          this.sendBuffer(this.bufferIndex)
        }
      }
    }
  }
  
  process(inputs, outputs, parameters) {
    const input = inputs[0]
    
    if (!this.isRecording || !input || !input[0]) {
      return true
    }
    
    // We'll only process the first channel for simplicity
    const inputChannel = input[0]
    
    for (let i = 0; i < inputChannel.length; i++) {
      this.buffer[this.bufferIndex++] = inputChannel[i]
      
      if (this.bufferIndex >= this.bufferSize) {
        this.sendBuffer(this.bufferSize)
        this.bufferIndex = 0
      }
    }
    
    // Pass through audio
    for (let channel = 0; channel < input.length; channel++) {
      const inputChannel = input[channel]
      const outputChannel = outputs[0][channel]
      
      if (inputChannel && outputChannel) {
        outputChannel.set(inputChannel)
      }
    }
    
    return true
  }
  
  sendBuffer(length) {
    // Create a copy of the buffer data to send
    const dataToSend = new Float32Array(length)
    for (let i = 0; i < length; i++) {
      dataToSend[i] = this.buffer[i]
    }
    
    this.port.postMessage({
      type: 'AUDIO_DATA',
      audioData: dataToSend,
      timestamp: this.currentTime
    })
  }
}

registerProcessor('audio-recorder-processor', AudioRecorderProcessor)