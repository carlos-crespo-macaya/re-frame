/**
 * Structured logging utility for the frontend
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  sessionId?: string;
  userId?: string;
  phase?: string;
  [key: string]: any;
}

class Logger {
  private name: string;
  private context: LogContext = {};
  private isProduction = process.env.NODE_ENV === 'production';

  constructor(name: string) {
    this.name = name;
  }

  setContext(context: Partial<LogContext>) {
    this.context = { ...this.context, ...context };
  }

  clearContext() {
    this.context = {};
  }

  private formatMessage(level: LogLevel, message: string, data?: any): any {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      logger: this.name,
      message,
      ...this.context,
      ...(data || {})
    };
    return logEntry;
  }

  private log(level: LogLevel, message: string, data?: any) {
    const logEntry = this.formatMessage(level, message, data);
    
    // In production, we might want to send logs to a service
    // For now, we'll use console methods
    switch (level) {
      case 'debug':
        if (!this.isProduction) {
          console.debug(message, logEntry);
        }
        break;
      case 'info':
        console.info(message, logEntry);
        break;
      case 'warn':
        console.warn(message, logEntry);
        break;
      case 'error':
        console.error(message, logEntry);
        break;
    }
  }

  debug(message: string, data?: any) {
    this.log('debug', message, data);
  }

  info(message: string, data?: any) {
    this.log('info', message, data);
  }

  warn(message: string, data?: any) {
    this.log('warn', message, data);
  }

  error(message: string, data?: any, error?: Error) {
    const errorData = {
      ...data,
      ...(error ? {
        errorName: error.name,
        errorMessage: error.message,
        errorStack: error.stack
      } : {})
    };
    this.log('error', message, errorData);
  }

  // Helper methods for common events
  sessionEvent(eventType: string, data?: any) {
    this.info('session_event', {
      eventType,
      ...data
    });
  }

  sseEvent(eventType: string, data?: any) {
    this.info('sse_event', {
      eventType,
      ...data
    });
  }

  audioEvent(eventType: string, data?: any) {
    this.info('audio_event', {
      eventType,
      ...data
    });
  }

  apiRequest(method: string, url: string, data?: any) {
    this.info('api_request', {
      method,
      url,
      ...data
    });
  }

  apiResponse(method: string, url: string, status: number, data?: any) {
    this.info('api_response', {
      method,
      url,
      status,
      ...data
    });
  }

  apiError(method: string, url: string, error: Error, data?: any) {
    this.error('api_error', {
      method,
      url,
      ...data
    }, error);
  }
}

export const createLogger = (name: string): Logger => {
  return new Logger(name);
};

// Create default loggers for common modules
export const sseLogger = createLogger('SSEClient');
export const audioLogger = createLogger('Audio');
export const apiLogger = createLogger('API');
export const appLogger = createLogger('App');