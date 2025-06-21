'use client'

import React, { Component, ReactNode, ErrorInfo } from 'react'
import ErrorFallback from './ErrorFallback'
import { errorLogger } from '@/lib/error-logger'

interface Props {
  children: ReactNode
  fallback?: React.ComponentType<{ error: Error; reset: () => void }>
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class RootErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error using our error logger
    errorLogger.logError(error, errorInfo)

    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  resetErrorBoundary = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || ErrorFallback

      return (
        <FallbackComponent 
          error={this.state.error} 
          reset={this.resetErrorBoundary}
        />
      )
    }

    return this.props.children
  }
}