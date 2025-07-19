'use client'

import { useEffect } from 'react'
import { setupAudioSimulation } from '@/test-utils/audio-helpers'

export function TestSetup() {
  useEffect(() => {
    // Only set up test helpers in test environments
    if (process.env.NODE_ENV === 'test' || process.env.NEXT_PUBLIC_E2E_TESTING === 'true') {
      setupAudioSimulation(window)
    }
  }, [])

  return null
}