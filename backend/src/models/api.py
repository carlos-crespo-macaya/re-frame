# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pydantic models for API request/response validation."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Service health status"
    )
    service: str = Field(
        default="CBT Reframing Assistant API", description="Service name"
    )
    timestamp: str = Field(..., description="Current UTC timestamp")
    version: str = Field(default="1.0.0", description="API version")


class MessageRequest(BaseModel):
    """Request model for sending messages to the agent."""

    mime_type: str = Field(..., description="MIME type of the message data")
    data: str = Field(..., description="Base64 encoded message data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mime_type": "text/plain",
                "data": "SGVsbG8gd29ybGQ=",  # "Hello world" in base64
            }
        }
    )


class MessageResponse(BaseModel):
    """Response model for message endpoints."""

    status: str = Field(..., description="Status of the message processing")
    error: str | None = Field(None, description="Error message if processing failed")

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "sent", "error": None}}
    )


class SessionInfo(BaseModel):
    """Information about a single session."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: str = Field(..., description="ISO format creation timestamp")
    last_activity: str = Field(..., description="ISO format last activity timestamp")
    age_seconds: float = Field(..., description="Age of session in seconds")
    inactive_seconds: float = Field(
        ..., description="Time since last activity in seconds"
    )
    has_request_queue: bool = Field(
        ..., description="Whether session has active request queue"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional session metadata"
    )


class SessionListResponse(BaseModel):
    """Response model for listing all sessions."""

    total_sessions: int = Field(..., description="Total number of active sessions")
    sessions: list[dict[str, Any]] = Field(..., description="List of session summaries")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_sessions": 2,
                "sessions": [
                    {
                        "session_id": "abc123",
                        "age_seconds": 120.5,
                        "inactive_seconds": 10.2,
                    }
                ],
            }
        }
    )


class SSEMessage(BaseModel):
    """Server-sent event message structure."""

    type: str = Field(..., description="Type of SSE message")
    session_id: str | None = Field(None, description="Session ID for connection events")
    message: str | None = Field(None, description="Message content for error events")
    turn_complete: bool | None = Field(
        None, description="Whether agent turn is complete"
    )
    interrupted: bool | None = Field(None, description="Whether agent was interrupted")
    content_type: str | None = Field(None, description="MIME type of content")
    data: str | None = Field(None, description="Base64 encoded content data")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"type": "connected", "session_id": "abc123"},
                {"type": "content", "content_type": "text/plain", "data": "SGVsbG8="},
                {"type": "turn_complete", "turn_complete": True, "interrupted": False},
            ]
        }
    )


class LanguageDetectionRequest(BaseModel):
    """Request model for language detection."""

    text: str = Field(..., description="Text to detect language from")

    model_config = ConfigDict(
        json_schema_extra={"example": {"text": "Hello, how are you today?"}}
    )


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection."""

    status: str = Field(..., description="Status of language detection")
    language: str | None = Field(
        None, description="Detected language code (e.g., 'en', 'es')"
    )
    confidence: float | None = Field(None, description="Confidence score (0-1)")
    message: str | None = Field(
        None, description="Additional information or error message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "language": "en",
                "confidence": 0.98,
                "message": None,
            }
        }
    )
