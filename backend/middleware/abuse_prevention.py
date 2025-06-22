"""Abuse prevention and content filtering middleware."""

import logging
import re
import time
from collections import defaultdict, deque

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ToxicContentError(HTTPException):
    """Exception raised when toxic content is detected."""

    def __init__(
        self,
        detail: str = "Content flagged as potentially harmful",
        toxicity_score: float = 0.0,
        categories: list[str] = None,
    ):
        super().__init__(status_code=400, detail=detail)
        self.toxicity_score = toxicity_score
        self.categories = categories or []


class ContentFilter:
    """Basic content filter for detecting harmful content."""

    def __init__(self):
        """Initialize content filter with basic patterns."""
        # Basic patterns for harmful content detection - optimized to prevent ReDoS
        # In production, use more sophisticated NLP models
        self.toxic_patterns = [
            # Self-harm related (fixed potential ReDoS)
            r"\b(?:kill myself|suicide|self.?harm|cut myself)\b",
            r"\b(?:want to die|better off dead)\b",
            # Violence (simplified to prevent backtracking)
            r"\b(?:kill|murder|hurt|harm|attack) (?:someone|people|them|him|her|you)\b",
            r"\bwant to (?:hurt|harm) ",
            r"\b(?:weapon|gun|knife|bomb)\b.{0,50}\b(?:use|get|make)\b",  # Limited quantifier
            # Hate speech (basic patterns)
            r"\b(?:hate|despise) (?:everyone|everything|all)\b",
            r"\bhate (?:myself|you|them)\b",
            r"\bI hate everything\b",
            # Extreme negativity
            r"\b(?:worthless|useless|pathetic|disgusting) (?:person|human|life)\b",
        ]

        # Compile patterns for efficiency with timeout protection
        self.compiled_patterns = []
        for pattern in self.toxic_patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self.compiled_patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                continue

    def is_toxic(self, text: str) -> bool:
        """Check if text contains toxic content.

        Args:
            text: Text to check

        Returns:
            True if toxic content detected, False otherwise
        """
        if not text or len(text) > 50000:  # Prevent processing of extremely long text
            return len(text) > 50000  # Consider very long text suspicious

        # Check against compiled patterns with timeout protection
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex timeout")
        
        # Set a timeout for regex operations (1 second)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)
        
        try:
            for pattern in self.compiled_patterns:
                if pattern.search(text):
                    return True
            return False
        except (TimeoutError, Exception):
            # If regex times out or fails, be conservative and flag as toxic
            logger.warning(f"Regex timeout or error while checking text: {text[:100]}...")
            return True
        finally:
            signal.alarm(0)  # Cancel the alarm

    def get_toxic_score(self, text: str) -> float:
        """Get toxicity score for text (0.0 to 1.0).

        Args:
            text: Text to score

        Returns:
            Toxicity score between 0.0 and 1.0
        """
        if not text:
            return 0.0

        # Count pattern matches
        matches = 0
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                matches += 1

        # Simple scoring based on matches
        # In production, use ML model for better scoring
        score = min(1.0, matches * 0.3)

        # Boost score for certain severe patterns
        severe_patterns = [
            r"\b(kill\s+myself|suicide)\b",
            r"\b(want\s+to\s+die)\b",
            r"\bhate\s+myself\b",  # Self-directed hate
        ]
        for pattern in severe_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score = min(1.0, score + 0.5)

        return score


class AbuseDetector:
    """Detector for abusive usage patterns."""

    def __init__(self, window_seconds: int = 300):
        """Initialize abuse detector.

        Args:
            window_seconds: Time window for pattern detection (default: 5 minutes)
        """
        self.window_seconds = window_seconds
        self.patterns_per_client: dict[str, deque[dict]] = defaultdict(deque)
        self.violation_counts: dict[str, list[dict]] = defaultdict(list)
        self.blocked_clients: set[str] = set()

    def track_request(self, client_id: str, path: str, method: str) -> None:
        """Track a request for pattern analysis.

        Args:
            client_id: Client identifier
            path: Request path
            method: HTTP method
        """
        current_time = time.time()

        # Add request to pattern tracking
        self.patterns_per_client[client_id].append(
            {"time": current_time, "path": path, "method": method}
        )

        # Cleanup old data
        self._cleanup_old_patterns(client_id, current_time)

    def track_violation(self, client_id: str, violation_type: str, details: str = "") -> None:
        """Track a violation by client.

        Args:
            client_id: Client identifier
            violation_type: Type of violation (e.g., "toxic_content", "rate_limit")
            details: Additional details about the violation
        """
        self.violation_counts[client_id].append(
            {"time": time.time(), "type": violation_type, "details": details}
        )

    def is_abusive_pattern(self, client_id: str) -> bool:
        """Check if client shows abusive request patterns.

        Args:
            client_id: Client identifier

        Returns:
            True if abusive pattern detected, False otherwise
        """
        patterns = self.patterns_per_client.get(client_id, deque())

        if len(patterns) < 5:
            return False

        # Check for suspicious patterns
        # 1. Too many different endpoints in short time (scanning)
        unique_paths = set(p["path"] for p in patterns)
        if len(unique_paths) > 15:
            return True

        # 2. Rapid-fire requests (faster than human)
        if len(patterns) >= 2:
            time_diffs = []
            for i in range(1, len(patterns)):
                diff = patterns[i]["time"] - patterns[i - 1]["time"]
                time_diffs.append(diff)

            # If average time between requests < 0.5 seconds
            avg_diff = sum(time_diffs) / len(time_diffs)
            if avg_diff < 0.5:
                return True

        return False

    def should_block_client(self, client_id: str) -> bool:
        """Check if client should be blocked.

        Args:
            client_id: Client identifier

        Returns:
            True if client should be blocked, False otherwise
        """
        if client_id in self.blocked_clients:
            return True

        violations = self.violation_counts.get(client_id, [])

        # Count recent violations
        current_time = time.time()
        recent_violations = [v for v in violations if current_time - v["time"] < 3600]  # Last hour

        # Block if too many violations
        if len(recent_violations) >= 5:
            self.blocked_clients.add(client_id)
            return True

        # Block if severe violations
        severe_violations = [
            v for v in recent_violations if v["type"] in ["toxic_content", "abuse_pattern"]
        ]
        if len(severe_violations) >= 3:
            self.blocked_clients.add(client_id)
            return True

        return False

    def get_violations(self, client_id: str) -> list[dict]:
        """Get violations for a client.

        Args:
            client_id: Client identifier

        Returns:
            List of violations
        """
        return self.violation_counts.get(client_id, [])

    def _cleanup_old_patterns(self, client_id: str, current_time: float) -> None:
        """Remove old pattern data outside the window."""
        patterns = self.patterns_per_client[client_id]
        cutoff_time = current_time - self.window_seconds

        while patterns and patterns[0]["time"] < cutoff_time:
            patterns.popleft()

        if not patterns:
            del self.patterns_per_client[client_id]

    def cleanup_old_data(self) -> None:
        """Cleanup old tracking data from all clients."""
        current_time = time.time()

        # Cleanup patterns
        for client_id in list(self.patterns_per_client.keys()):
            self._cleanup_old_patterns(client_id, current_time)

        # Cleanup old violations (keep for 24 hours)
        cutoff_time = current_time - 86400
        for client_id in list(self.violation_counts.keys()):
            violations = self.violation_counts[client_id]
            self.violation_counts[client_id] = [v for v in violations if v["time"] > cutoff_time]
            if not self.violation_counts[client_id]:
                del self.violation_counts[client_id]


class AbusePreventionMiddleware(BaseHTTPMiddleware):
    """Middleware for preventing abuse and filtering toxic content."""

    # Paths exempt from abuse checks
    EXEMPT_PATHS = {"/health", "/api/v1/health", "/docs", "/openapi.json"}

    def __init__(
        self,
        app: ASGIApp,
        enable_perspective_api: bool = False,
        perspective_api_key: str | None = None,
        toxicity_threshold: float = 0.7,
    ):
        """Initialize abuse prevention middleware.

        Args:
            app: ASGI application
            enable_perspective_api: Whether to use Google Perspective API
            perspective_api_key: API key for Perspective API
            toxicity_threshold: Threshold for toxic content (0.0-1.0)
        """
        super().__init__(app)
        self.content_filter = ContentFilter()
        self.abuse_detector = AbuseDetector()
        self.enable_perspective_api = enable_perspective_api
        self.perspective_api_key = perspective_api_key
        self.toxicity_threshold = toxicity_threshold

        if enable_perspective_api:
            if not perspective_api_key:
                logger.warning("Perspective API enabled but no API key provided")
                self.enable_perspective_api = False
            elif not self._validate_perspective_api_key(perspective_api_key):
                logger.warning("Invalid Perspective API key format")
                self.enable_perspective_api = False

        logger.info(f"Abuse prevention initialized. Perspective API: {self.enable_perspective_api}")

    def _validate_perspective_api_key(self, api_key: str) -> bool:
        """Validate Perspective API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if key format is valid, False otherwise
        """
        # Basic validation - Google API keys typically start with certain prefixes
        # and have specific length requirements
        if not api_key or len(api_key) < 20:
            return False
            
        # Google API keys often start with 'AIza' but can vary
        # This is a basic check to catch obvious errors
        import re
        pattern = r'^[A-Za-z0-9_-]{20,}$'
        return re.match(pattern, api_key) is not None

    async def dispatch(self, request: Request, call_next):
        """Process request with abuse prevention checks."""
        # Skip checks for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Get client identifier
        from .rate_limiting import get_client_ip

        client_id = get_client_ip(request)

        # Check if client is blocked
        if self.abuse_detector.should_block_client(client_id):
            logger.warning(f"Blocked client {client_id} attempted access")
            return Response(content="Access denied due to policy violations", status_code=403)

        # Track request pattern
        self.abuse_detector.track_request(client_id, request.url.path, request.method)

        # Check for abusive patterns
        if self.abuse_detector.is_abusive_pattern(client_id):
            self.abuse_detector.track_violation(client_id, "abuse_pattern")
            logger.warning(f"Abusive pattern detected for client {client_id}")
            return Response(content="Unusual activity detected. Please slow down.", status_code=429)

        # For POST requests, check content
        if request.method == "POST" and request.url.path == "/api/v1/reframe":
            try:
                # Read request body with size limit
                body = await request.body()
                
                # Check payload size (50KB limit)
                if len(body) > 50000:
                    logger.warning(f"Payload too large from {client_id}: {len(body)} bytes")
                    return Response("Payload too large", status_code=413)

                # Parse JSON safely
                import json

                try:
                    data = json.loads(body)
                    if not isinstance(data, dict):
                        return Response("Invalid JSON structure", status_code=400)
                    
                    thought = data.get("thought", "")
                    if not isinstance(thought, str):
                        return Response("Invalid thought format", status_code=400)
                        
                except json.JSONDecodeError:
                    return Response("Invalid JSON", status_code=400)
                except Exception:
                    thought = ""

                # Check content toxicity
                toxicity_score = await self._check_toxicity(thought)

                if toxicity_score >= self.toxicity_threshold:
                    self.abuse_detector.track_violation(
                        client_id, "toxic_content", f"score: {toxicity_score}"
                    )
                    logger.warning(
                        f"Toxic content blocked from {client_id}: score {toxicity_score}"
                    )
                    return Response(
                        content="Content flagged as potentially harmful. "
                        "Please rephrase in a constructive way.",
                        status_code=400,
                        headers={"X-Toxicity-Score": str(toxicity_score)},
                    )

                # Add toxicity score to response headers
                response = await call_next(request)
                response.headers["X-Abuse-Score"] = str(toxicity_score)
                return response

            except Exception as e:
                logger.error(f"Error in abuse prevention: {e}")
                # On error, allow request but log it
                return await call_next(request)

        # For other requests, just pass through
        return await call_next(request)

    async def _check_toxicity(self, text: str) -> float:
        """Check text toxicity using local filter and optionally Perspective API.

        Args:
            text: Text to check

        Returns:
            Toxicity score (0.0 to 1.0)
        """
        # First check with local filter
        local_score = self.content_filter.get_toxic_score(text)

        # If local score is high or Perspective API disabled, return local score
        if local_score >= 0.7 or not self.enable_perspective_api:
            return local_score

        # Check with Perspective API for additional validation
        try:
            perspective_score = await self._check_perspective_api(text)
            # Return average of both scores
            return (local_score + perspective_score) / 2
        except Exception as e:
            logger.error(f"Perspective API error: {e}")
            # Fall back to local score
            return local_score

    async def _check_perspective_api(self, text: str) -> float:
        """Check text with Google Perspective API.

        Args:
            text: Text to analyze

        Returns:
            Toxicity score from Perspective API
        """
        url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

        payload = {
            "comment": {"text": text},
            "requestedAttributes": {
                "TOXICITY": {},
                "SEVERE_TOXICITY": {},
                "THREAT": {},
                "INSULT": {},
            },
        }

        params = {"key": self.perspective_api_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, params=params, timeout=5.0)
            response.raise_for_status()

            result = response.json()
            scores = result.get("attributeScores", {})

            # Get max score from all attributes
            max_score = 0.0
            for attr in ["TOXICITY", "SEVERE_TOXICITY", "THREAT", "INSULT"]:
                if attr in scores:
                    score = scores[attr]["summaryScore"]["value"]
                    max_score = max(max_score, score)

            return max_score
