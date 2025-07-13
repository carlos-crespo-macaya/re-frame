class NoiseGateProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
      {
        name: 'threshold',
        defaultValue: -50,
        minValue: -100,
        maxValue: 0,
        automationRate: 'k-rate'
      },
      {
        name: 'attack',
        defaultValue: 0.003,
        minValue: 0,
        maxValue: 0.1,
        automationRate: 'k-rate'
      },
      {
        name: 'release',
        defaultValue: 0.1,
        minValue: 0,
        maxValue: 1,
        automationRate: 'k-rate'
      }
    ]
  }

  constructor() {
    super()
    this.isOpen = false
    this.envelope = 0
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0]
    const output = outputs[0]
    
    if (!input || !input[0]) {
      return true
    }

    const threshold = Math.pow(10, parameters.threshold[0] / 20)
    const attack = parameters.attack[0]
    const release = parameters.release[0]
    
    for (let channel = 0; channel < input.length; channel++) {
      const inputChannel = input[channel]
      const outputChannel = output[channel]
      
      for (let i = 0; i < inputChannel.length; i++) {
        const inputSample = inputChannel[i]
        const inputLevel = Math.abs(inputSample)
        
        // Update envelope
        const targetEnvelope = inputLevel > threshold ? 1 : 0
        const rate = targetEnvelope > this.envelope ? attack : release
        this.envelope += (targetEnvelope - this.envelope) * rate
        
        // Apply gate
        outputChannel[i] = inputSample * this.envelope
      }
    }
    
    // Send gate state to main thread
    if (this.envelope > 0.5 !== this.isOpen) {
      this.isOpen = this.envelope > 0.5
      this.port.postMessage({ type: 'gateState', isOpen: this.isOpen })
    }
    
    return true
  }
}

registerProcessor('noise-gate-processor', NoiseGateProcessor)