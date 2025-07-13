/**
 * Session management for SSE connections
 */

import { v4 as uuidv4 } from 'uuid';

export interface Session {
  id: string;
  createdAt: Date;
  lastActivity: Date;
  isActive: boolean;
  metadata?: Record<string, any>;
}

export class SessionManager {
  private sessions: Map<string, Session> = new Map();
  private activeSessionId: string | null = null;
  
  /**
   * Create a new session
   */
  createSession(metadata?: Record<string, any>): Session {
    const session: Session = {
      id: uuidv4(),
      createdAt: new Date(),
      lastActivity: new Date(),
      isActive: true,
      metadata
    };
    
    this.sessions.set(session.id, session);
    this.activeSessionId = session.id;
    
    return session;
  }
  
  /**
   * Get a session by ID
   */
  getSession(sessionId: string): Session | undefined {
    return this.sessions.get(sessionId);
  }
  
  /**
   * Get the active session
   */
  getActiveSession(): Session | null {
    if (!this.activeSessionId) return null;
    return this.sessions.get(this.activeSessionId) || null;
  }
  
  /**
   * Update session activity
   */
  updateActivity(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastActivity = new Date();
    }
  }
  
  /**
   * Set active session
   */
  setActiveSession(sessionId: string): boolean {
    if (this.sessions.has(sessionId)) {
      this.activeSessionId = sessionId;
      return true;
    }
    return false;
  }
  
  /**
   * Deactivate a session
   */
  deactivateSession(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isActive = false;
      if (this.activeSessionId === sessionId) {
        this.activeSessionId = null;
      }
    }
  }
  
  /**
   * Remove a session
   */
  removeSession(sessionId: string): boolean {
    if (this.activeSessionId === sessionId) {
      this.activeSessionId = null;
    }
    return this.sessions.delete(sessionId);
  }
  
  /**
   * Clean up inactive sessions older than maxAge
   */
  cleanupSessions(maxAgeMs: number = 3600000): number {
    const now = Date.now();
    let removed = 0;
    
    this.sessions.forEach((session, id) => {
      const age = now - session.lastActivity.getTime();
      if (!session.isActive && age > maxAgeMs) {
        this.removeSession(id);
        removed++;
      }
    });
    
    return removed;
  }
  
  /**
   * Get all active sessions
   */
  getActiveSessions(): Session[] {
    return Array.from(this.sessions.values()).filter(s => s.isActive);
  }
  
  /**
   * Clear all sessions
   */
  clearAll(): void {
    this.sessions.clear();
    this.activeSessionId = null;
  }
}

// Singleton instance
export const sessionManager = new SessionManager();