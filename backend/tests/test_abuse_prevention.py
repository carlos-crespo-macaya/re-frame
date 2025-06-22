"""Tests for abuse prevention and content filtering."""

from unittest.mock import AsyncMock, patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from middleware.abuse_prevention import (
    AbuseDetector,
    AbusePreventionMiddleware,
    ContentFilter,
    ToxicContentError,
)


class TestContentFilter:
    """Test the ContentFilter class."""

    def test_initialization(self):
        """Test ContentFilter initialization."""
        filter = ContentFilter()
        assert filter.toxic_patterns is not None
        assert len(filter.toxic_patterns) > 0

    def test_is_toxic_clean_content(self):
        """Test that clean content passes filter."""
        filter = ContentFilter()

        clean_texts = [
            "I'm feeling anxious about my presentation",
            "I think I made a mistake at work",
            "I'm worried about what others think of me",
            "I feel like I'm not good enough sometimes",
        ]

        for text in clean_texts:
            assert filter.is_toxic(text) is False

    def test_is_toxic_harmful_content(self):
        """Test that harmful content is detected."""
        filter = ContentFilter()

        # Note: Using mild examples for testing
        toxic_texts = [
            "I hate myself",
            "I want to hurt someone",
            "I want to kill myself",  # Clear self-harm content
        ]

        for text in toxic_texts:
            assert filter.is_toxic(text) is True

    def test_get_toxic_score(self):
        """Test toxicity scoring."""
        filter = ContentFilter()

        # Clean content should have low score
        assert filter.get_toxic_score("I'm feeling worried") < 0.3

        # Toxic content should have high score
        assert filter.get_toxic_score("I hate everything") > 0.5


class TestAbuseDetector:
    """Test the AbuseDetector class."""

    def test_initialization(self):
        """Test AbuseDetector initialization."""
        detector = AbuseDetector()
        assert detector.patterns_per_client is not None
        assert detector.violation_counts is not None

    def test_track_request_normal_pattern(self):
        """Test tracking normal request patterns."""
        detector = AbuseDetector()

        # Normal usage pattern
        detector.track_request("client1", "/api/v1/reframe", "POST")
        detector.track_request("client1", "/api/v1/reframe", "POST")

        assert detector.is_abusive_pattern("client1") is False

    def test_track_request_suspicious_pattern(self):
        """Test detecting suspicious request patterns."""
        detector = AbuseDetector()

        # Rapid requests to different endpoints
        for i in range(20):
            detector.track_request("client1", f"/api/v1/endpoint{i}", "GET")

        assert detector.is_abusive_pattern("client1") is True

    def test_track_violation(self):
        """Test tracking violations."""
        detector = AbuseDetector()

        # Track violations
        detector.track_violation("client1", "toxic_content")
        detector.track_violation("client1", "rate_limit")

        violations = detector.get_violations("client1")
        assert len(violations) == 2
        assert violations[0]["type"] == "toxic_content"
        assert violations[1]["type"] == "rate_limit"

    def test_should_block_client(self):
        """Test client blocking logic."""
        detector = AbuseDetector()

        # Client with few violations should not be blocked
        detector.track_violation("client1", "rate_limit")
        assert detector.should_block_client("client1") is False

        # Client with many violations should be blocked
        for _ in range(5):
            detector.track_violation("client2", "toxic_content")
        assert detector.should_block_client("client2") is True

    def test_cleanup_old_data(self):
        """Test cleanup of old tracking data."""
        detector = AbuseDetector()

        # Track some data
        detector.track_request("client1", "/api/v1/reframe", "POST")
        detector.track_violation("client1", "rate_limit")

        # Cleanup should not affect recent data
        detector.cleanup_old_data()
        assert len(detector.patterns_per_client) > 0
        assert len(detector.violation_counts) > 0


class TestAbusePreventionMiddleware:
    """Test the AbusePreventionMiddleware."""

    def create_test_app(self, enable_perspective_api=False):
        """Create a test FastAPI app with abuse prevention middleware."""
        app = FastAPI()

        # Add abuse prevention middleware
        app.add_middleware(AbusePreventionMiddleware, enable_perspective_api=enable_perspective_api)

        @app.post("/api/v1/reframe")
        async def reframe_endpoint(request: Request):
            body = await request.json()
            return {"thought": body.get("thought", ""), "reframed": "positive version"}

        @app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}

        return TestClient(app)

    def test_middleware_allows_clean_requests(self):
        """Test that middleware allows clean requests."""
        client = self.create_test_app()

        response = client.post(
            "/api/v1/reframe", json={"thought": "I'm worried about my presentation"}
        )
        assert response.status_code == 200
        assert response.json()["reframed"] == "positive version"

    def test_middleware_blocks_toxic_content(self):
        """Test that middleware blocks toxic content."""
        client = self.create_test_app()

        response = client.post(
            "/api/v1/reframe", json={"thought": "I hate everything and want to hurt people"}
        )
        assert response.status_code == 400
        assert "harmful" in response.text.lower()

    def test_middleware_tracks_violations(self):
        """Test that middleware tracks violations."""
        client = self.create_test_app()

        # Send toxic content multiple times
        for _ in range(3):
            response = client.post("/api/v1/reframe", json={"thought": "I hate myself"})
            assert response.status_code == 400

    def test_health_endpoint_exempt(self):
        """Test that health endpoint is exempt from abuse checks."""
        client = self.create_test_app()

        # Health endpoint should always work
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @patch("httpx.AsyncClient.post")
    async def test_perspective_api_integration(self, mock_post):
        """Test Perspective API integration when enabled."""
        # Mock Perspective API response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "attributeScores": {"TOXICITY": {"summaryScore": {"value": 0.8}}}
        }
        mock_post.return_value = mock_response

        # Create app with valid format mock API key
        app = FastAPI()
        app.add_middleware(
            AbusePreventionMiddleware,
            enable_perspective_api=True,
            perspective_api_key="AIzaSyDxKXxXxXxXxXxXxXxXxXxXxXxXxXxXxX",  # Valid format mock key
        )

        @app.post("/api/v1/reframe")
        async def reframe_endpoint(request: Request):
            body = await request.json()
            return {"thought": body.get("thought", ""), "reframed": "positive version"}

        client = TestClient(app)

        response = client.post("/api/v1/reframe", json={"thought": "This is a test thought"})

        # Should check with Perspective API
        mock_post.assert_called_once()

    def test_abuse_prevention_headers(self):
        """Test that abuse prevention headers are included."""
        client = self.create_test_app()

        response = client.post("/api/v1/reframe", json={"thought": "Normal thought"})

        assert "X-Abuse-Score" in response.headers
        assert float(response.headers["X-Abuse-Score"]) < 0.5


class TestToxicContentError:
    """Test the ToxicContentError exception."""

    def test_exception_attributes(self):
        """Test ToxicContentError exception attributes."""
        exc = ToxicContentError(
            detail="Content flagged as toxic", toxicity_score=0.85, categories=["hate", "violence"]
        )

        assert exc.detail == "Content flagged as toxic"
        assert exc.toxicity_score == 0.85
        assert exc.categories == ["hate", "violence"]
        assert exc.status_code == 400
