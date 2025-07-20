/**
 * Central API client for all backend communication
 */

import { API_CONFIG } from './config'
import { ApiError, logApiError } from './errors'
import type {
  EventSourceParams,
  PdfDownloadResponse,
  MessageData,
  ApiRequestConfig
} from './types'
import { apiLogger } from '../logger'
import { generatedApi } from './generated-client'
import type { CreateVoiceSessionRequest } from './generated-client'

/**
 * Main API client class
 */
export class ApiClient {
  /**
   * Perform a fetch request with error handling
   */
  private static async fetchWithTimeout(
    url: string,
    config: ApiRequestConfig = {}
  ): Promise<Response> {
    const { timeout = API_CONFIG.timeouts.default, ...fetchConfig } = config

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      apiLogger.apiRequest(fetchConfig.method || 'GET', url, {
        timeout,
        headers: fetchConfig.headers
      })
      
      const response = await fetch(url, {
        ...fetchConfig,
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      
      apiLogger.apiResponse(fetchConfig.method || 'GET', url, response.status, {
        ok: response.ok,
        statusText: response.statusText
      })
      
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          apiLogger.apiError(fetchConfig.method || 'GET', url, error, {
            reason: 'timeout',
            timeout
          })
          throw new ApiError(408, 'Request timeout')
        }
      }
      apiLogger.apiError(fetchConfig.method || 'GET', url, error as Error)
      throw error
    }
  }

  /**
   * Handle API response and check for errors
   */
  private static async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let details: unknown
      try {
        details = await response.json()
      } catch {
        // Response might not be JSON
      }
      throw new ApiError(response.status, response.statusText, details)
    }

    // Handle empty responses
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      // For void returns, we can safely return undefined
      // The caller should expect void for these responses
      return undefined as unknown as T
    }

    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      return response.json()
    }

    // For non-JSON responses, throw an error as we expect JSON
    throw new ApiError(
      415,
      `Unsupported content type: ${contentType || 'unknown'}`,
      { contentType }
    )
  }

  /**
   * Send a message to the backend
   */
  static async sendMessage(
    sessionId: string,
    data: MessageData
  ): Promise<void> {
    const url = `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.send(sessionId)}`
    
    try {
      const response = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: API_CONFIG.defaultHeaders,
        body: JSON.stringify(data)
      })

      await this.handleResponse<void>(response)
    } catch (error) {
      logApiError(error, `sendMessage(${sessionId})`)
      throw error
    }
  }

  /**
   * Create an EventSource for SSE streaming
   */
  static createEventSource(
    sessionId: string,
    params?: EventSourceParams
  ): EventSource {
    const url = new URL(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.events(sessionId)}`)
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    return new EventSource(url.toString())
  }

  /**
   * Download a PDF for a session
   */
  static async downloadPdf(sessionId: string): Promise<PdfDownloadResponse> {
    const url = `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.pdf(sessionId)}`
    
    try {
      const response = await this.fetchWithTimeout(url, {
        timeout: API_CONFIG.timeouts.upload
      })

      if (!response.ok) {
        throw new ApiError(response.status, response.statusText)
      }

      const blob = await response.blob()
      
      // Extract filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('content-disposition')
      let filename = `session-${sessionId}.pdf`
      
      if (contentDisposition) {
        // Handle different Content-Disposition formats:
        // filename="example.pdf"
        // filename=example.pdf
        // filename*=UTF-8''example.pdf
        const filenameMatch = contentDisposition.match(
          /filename\*?=["']?(?:UTF-8'')?([^;\n"']+)["']?/i
        )
        if (filenameMatch && filenameMatch[1]) {
          // Decode URL-encoded filenames and remove quotes
          filename = decodeURIComponent(filenameMatch[1].replace(/["']/g, ''))
        }
      }

      return { blob, filename }
    } catch (error) {
      logApiError(error, `downloadPdf(${sessionId})`)
      throw error
    }
  }

  /**
   * Check API health
   */
  static async checkHealth(): Promise<boolean> {
    try {
      const response = await this.fetchWithTimeout(
        `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.health}`,
        { timeout: 5000 }
      )
      return response.ok
    } catch {
      return false
    }
  }

  /**
   * Create a voice session
   */
  static async createVoiceSession(language: string = 'en-US'): Promise<{ session_id: string; status: string; language: string }> {
    try {
      const request: CreateVoiceSessionRequest = { language }
      const response = await generatedApi.voice.createSession(request)
      return response
    } catch (error) {
      logApiError(error, 'createVoiceSession')
      throw error
    }
  }

  /**
   * Send audio chunk to voice session
   */
  static async sendVoiceAudio(
    sessionId: string,
    audioData: string,
    turnComplete: boolean = false,
    sampleRate: number = 48000
  ): Promise<void> {
    try {
      // Send audio data with timestamp and sample rate
      await generatedApi.voice.sendAudio(sessionId, {
        data: audioData,
        timestamp: Date.now(),
        sample_rate: sampleRate
      })
      
      // If turn complete, send control command
      if (turnComplete) {
        await generatedApi.voice.sendControl(sessionId, {
          action: 'end_turn'
        })
      }
    } catch (error) {
      logApiError(error, `sendVoiceAudio(${sessionId})`)
      throw error
    }
  }

  /**
   * Create voice EventSource for SSE streaming
   */
  static createVoiceEventSource(sessionId: string): EventSource {
    const url = `${API_CONFIG.baseUrl}${generatedApi.voice.getStreamEndpoint(sessionId)}`
    
    apiLogger.info('SSE connection start', { url })
    
    const eventSource = new EventSource(url)
    
    // Add basic event listeners for debugging
    eventSource.addEventListener('open', () => {
      apiLogger.info('SSE connection opened', { url })
    })
    
    eventSource.addEventListener('error', (error) => {
      apiLogger.error('SSE connection error', { url }, new Error(`SSE connection failed: ${error.type}`))
    })
    
    return eventSource
  }
}

/**
 * Convenience function for sending messages
 */
export async function sendMessage(
  sessionId: string,
  data: MessageData
): Promise<void> {
  return ApiClient.sendMessage(sessionId, data)
}

/**
 * Convenience function for creating EventSource
 */
export function createEventSource(
  sessionId: string,
  params?: EventSourceParams
): EventSource {
  return ApiClient.createEventSource(sessionId, params)
}

/**
 * Convenience function for downloading PDFs
 */
export async function downloadPdf(sessionId: string): Promise<PdfDownloadResponse> {
  return ApiClient.downloadPdf(sessionId)
}