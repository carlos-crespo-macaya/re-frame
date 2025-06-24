"""Load testing scenarios for the re-frame API."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import time
from typing import Any

from faker import Faker
import httpx
import pytest

from tests.fixtures.test_data_generator import (
    ThoughtGenerator,
    generate_batch_requests,
    generate_test_request,
)

fake = Faker()


class LoadTestMetrics:
    """Track and calculate load test metrics."""

    def __init__(self):
        self.response_times: list[float] = []
        self.status_codes: dict[int, int] = {}
        self.errors: list[str] = []
        self.start_time = time.time()

    def record_response(self, response_time: float, status_code: int, error: str | None = None):
        """Record a response."""
        self.response_times.append(response_time)
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        if error:
            self.errors.append(error)

    def get_summary(self) -> dict[str, Any]:
        """Get summary metrics."""
        if not self.response_times:
            return {"error": "No responses recorded"}

        total_time = time.time() - self.start_time
        total_requests = len(self.response_times)

        return {
            "total_requests": total_requests,
            "total_time": round(total_time, 2),
            "requests_per_second": round(total_requests / total_time, 2),
            "avg_response_time": round(statistics.mean(self.response_times), 3),
            "min_response_time": round(min(self.response_times), 3),
            "max_response_time": round(max(self.response_times), 3),
            "p50_response_time": round(statistics.median(self.response_times), 3),
            "p95_response_time": (
                round(statistics.quantiles(self.response_times, n=20)[18], 3)
                if len(self.response_times) > 20
                else None
            ),
            "p99_response_time": (
                round(statistics.quantiles(self.response_times, n=100)[98], 3)
                if len(self.response_times) > 100
                else None
            ),
            "status_codes": self.status_codes,
            "error_count": len(self.errors),
            "success_rate": round((self.status_codes.get(200, 0) / total_requests) * 100, 2),
        }


class LoadTester:
    """Perform load testing against the API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = LoadTestMetrics()

    def make_request(self, endpoint: str, data: dict[str, Any]) -> None:
        """Make a single request and record metrics."""
        start_time = time.time()

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    timeout=10.0,
                )
                response_time = time.time() - start_time
                self.metrics.record_response(response_time, response.status_code)

        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_response(response_time, 0, str(e))

    def run_concurrent_requests(self, num_requests: int, max_workers: int = 10) -> dict[str, Any]:
        """Run concurrent requests."""
        requests = generate_batch_requests(num_requests)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.make_request, "/api/reframe/", request) for request in requests
            ]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.metrics.errors.append(str(e))

        return self.metrics.get_summary()

    async def run_burst_test(
        self, burst_size: int, num_bursts: int, delay_between_bursts: float
    ) -> dict[str, Any]:
        """Run burst load test - sudden spikes of traffic."""
        results = []

        for i in range(num_bursts):
            print(f"Running burst {i+1}/{num_bursts}...")
            burst_metrics = LoadTestMetrics()
            self.metrics = burst_metrics

            # Send burst
            burst_result = self.run_concurrent_requests(burst_size, max_workers=burst_size)
            results.append(burst_result)

            # Wait between bursts
            if i < num_bursts - 1:
                await asyncio.sleep(delay_between_bursts)

        return {
            "burst_size": burst_size,
            "num_bursts": num_bursts,
            "delay_between_bursts": delay_between_bursts,
            "burst_results": results,
            "overall_success_rate": statistics.mean([r["success_rate"] for r in results]),
        }

    async def run_sustained_load_test(
        self, requests_per_second: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Run sustained load test - constant rate over time."""
        start_time = time.time()
        request_interval = 1.0 / requests_per_second
        total_requests = 0

        while time.time() - start_time < duration_seconds:
            # Send request
            request = generate_test_request()
            asyncio.create_task(self._async_request("/api/reframe/", request))
            total_requests += 1

            # Wait for next request slot
            await asyncio.sleep(request_interval)

        # Wait for all requests to complete
        await asyncio.sleep(5)

        summary = self.metrics.get_summary()
        summary["target_rps"] = requests_per_second
        summary["actual_rps"] = round(total_requests / duration_seconds, 2)

        return summary

    async def _async_request(self, endpoint: str, data: dict[str, Any]) -> None:
        """Make async request."""
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    timeout=10.0,
                )
                response_time = time.time() - start_time
                self.metrics.record_response(response_time, response.status_code)

            except Exception as e:
                response_time = time.time() - start_time
                self.metrics.record_response(response_time, 0, str(e))


@pytest.mark.load
class TestLoadScenarios:
    """Load testing scenarios."""

    @pytest.fixture
    def load_tester(self):
        """Create load tester instance."""
        return LoadTester()

    def test_basic_load(self, load_tester):
        """Test basic load - 100 concurrent users."""
        result = load_tester.run_concurrent_requests(
            num_requests=100,
            max_workers=100,
        )

        print("\nBasic Load Test Results:")
        print(f"Total requests: {result['total_requests']}")
        print(f"Success rate: {result['success_rate']}%")
        print(f"Avg response time: {result['avg_response_time']}s")
        print(f"Max response time: {result['max_response_time']}s")

        # Assertions
        assert result["success_rate"] > 90, "Success rate should be above 90%"
        assert result["avg_response_time"] < 2.0, "Average response time should be under 2 seconds"

    def test_rate_limit_behavior(self, load_tester):
        """Test rate limiting behavior."""
        # Send 15 requests rapidly (limit is 10/hour per IP)
        result = load_tester.run_concurrent_requests(
            num_requests=15,
            max_workers=1,  # Sequential to ensure same IP
        )

        # Should see 429 status codes
        assert 429 in result["status_codes"], "Should hit rate limits"
        assert result["status_codes"].get(429, 0) >= 5, "At least 5 requests should be rate limited"

    @pytest.mark.asyncio
    async def test_burst_traffic(self, load_tester):
        """Test burst traffic pattern."""
        result = await load_tester.run_burst_test(
            burst_size=50,
            num_bursts=3,
            delay_between_bursts=5.0,
        )

        print("\nBurst Traffic Test Results:")
        print(f"Overall success rate: {result['overall_success_rate']}%")

        # System should handle bursts gracefully
        assert result["overall_success_rate"] > 80, "Should handle burst traffic with >80% success"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load(self, load_tester):
        """Test sustained load over time."""
        result = await load_tester.run_sustained_load_test(
            requests_per_second=5,
            duration_seconds=60,  # 1 minute
        )

        print("\nSustained Load Test Results:")
        print(f"Target RPS: {result['target_rps']}")
        print(f"Actual RPS: {result['actual_rps']}")
        print(f"Success rate: {result['success_rate']}%")
        print(f"P95 response time: {result.get('p95_response_time', 'N/A')}s")

        # Should maintain performance under sustained load
        assert result["success_rate"] > 95, "Should maintain >95% success rate"
        assert result["p95_response_time"] < 3.0, "P95 response time should be under 3 seconds"

    def test_mixed_traffic_patterns(self, load_tester):
        """Test mixed traffic patterns (normal + crisis + toxic)."""
        requests = []

        # Normal thoughts
        for _ in range(70):
            requests.append(generate_test_request())

        # Crisis thoughts
        for _ in range(20):
            requests.append({"thought": ThoughtGenerator.generate_crisis_thought()})

        # Potentially toxic thoughts
        for _ in range(10):
            requests.append({"thought": "I hate everyone and want them to suffer"})

        # Run test with mixed traffic
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(load_tester.make_request, "/api/reframe/", request)
                for request in requests
            ]

            for future in as_completed(futures):
                future.result()

        result = load_tester.metrics.get_summary()

        print("\nMixed Traffic Test Results:")
        print(f"Total requests: {result['total_requests']}")
        print(f"Success rate: {result['success_rate']}%")
        print(f"Status codes: {result['status_codes']}")

        # Should handle all types of traffic
        assert result["total_requests"] == 100
        assert result["success_rate"] > 85, "Should handle mixed traffic patterns"

    def test_error_recovery(self, load_tester):
        """Test system recovery from errors."""
        # Send some malformed requests
        bad_requests = [
            {},  # Empty request
            {"thought": ""},  # Empty thought
            {"thought": "x"},  # Too short
            {"thought": "x" * 3000},  # Too long
            {"invalid_field": "test"},  # Invalid field
        ]

        for request in bad_requests:
            load_tester.make_request("/api/reframe/", request)

        # Then send valid requests
        valid_requests = generate_batch_requests(10)
        for request in valid_requests:
            load_tester.make_request("/api/reframe/", request)

        result = load_tester.metrics.get_summary()

        # Should see both 422 (validation) and 200 (success) codes
        assert 422 in result["status_codes"], "Should have validation errors"
        assert 200 in result["status_codes"], "Should recover and process valid requests"
        assert result["status_codes"][200] == 10, "All valid requests should succeed"


@pytest.mark.load
@pytest.mark.benchmark
def test_response_time_benchmark(benchmark):
    """Benchmark individual request response time."""
    client = httpx.Client(base_url="http://localhost:8000")
    request_data = generate_test_request()

    def make_request():
        response = client.post("/api/reframe/", json=request_data)
        return response

    # Run benchmark
    result = benchmark(make_request)

    # Response should be successful
    assert result.status_code == 200
