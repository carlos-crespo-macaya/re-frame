#!/usr/bin/env python3
"""Manual load testing script for voice modality."""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import from tests
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import httpx
from tests.fixtures import AudioSamples


async def simulate_voice_user(
    client: httpx.AsyncClient, user_id: int, audio_sample: str = "hello"
) -> tuple[int, float]:
    """Simulate a single voice user interaction."""
    session_id = f"load-test-{user_id}-{int(time.time())}"
    audio_data = AudioSamples.get_sample(audio_sample)

    start_time = time.time()
    try:
        response = await client.post(
            f"/api/send/{session_id}",
            json={"mime_type": "audio/pcm", "data": audio_data},
            timeout=30.0,
        )
        elapsed = time.time() - start_time
        return response.status_code, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"User {user_id} error: {e}")
        return 500, elapsed


async def run_concurrent_test(
    base_url: str, num_users: int, iterations: int = 1
) -> None:
    """Run concurrent user test."""
    print(f"\n🚀 Starting concurrent test: {num_users} users, {iterations} iterations")

    async with httpx.AsyncClient(base_url=base_url) as client:
        total_requests = 0
        total_success = 0
        all_response_times = []

        for iteration in range(iterations):
            print(f"\n📊 Iteration {iteration + 1}/{iterations}")
            
            # Create tasks for concurrent users
            tasks = [
                simulate_voice_user(client, user_id + (iteration * num_users))
                for user_id in range(num_users)
            ]

            # Execute concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            iteration_time = time.time() - start_time

            # Analyze results
            successful = [
                r for r in results if isinstance(r, tuple) and r[0] == 200
            ]
            failed = len(results) - len(successful)

            response_times = [r[1] for r in successful]
            all_response_times.extend(response_times)

            total_requests += len(results)
            total_success += len(successful)

            # Print iteration stats
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                print(f"  ✅ Success: {len(successful)}/{len(results)}")
                print(f"  ⏱️  Response times - Min: {min_time:.2f}s, Avg: {avg_time:.2f}s, Max: {max_time:.2f}s")
                print(f"  🏁 Iteration completed in {iteration_time:.2f}s")
            else:
                print(f"  ❌ All requests failed!")

            # Brief pause between iterations
            if iteration < iterations - 1:
                await asyncio.sleep(2)

    # Final summary
    print("\n" + "=" * 50)
    print("📈 FINAL RESULTS")
    print("=" * 50)
    print(f"Total requests: {total_requests}")
    print(f"Successful: {total_success}")
    print(f"Failed: {total_requests - total_success}")
    print(f"Success rate: {(total_success / total_requests * 100):.1f}%")

    if all_response_times:
        all_response_times.sort()
        avg_time = sum(all_response_times) / len(all_response_times)
        p50 = all_response_times[int(len(all_response_times) * 0.50)]
        p95 = all_response_times[int(len(all_response_times) * 0.95)]
        p99 = all_response_times[int(len(all_response_times) * 0.99)]

        print(f"\nResponse time percentiles:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  P50: {p50:.3f}s")
        print(f"  P95: {p95:.3f}s")
        print(f"  P99: {p99:.3f}s")


async def run_sustained_test(
    base_url: str, duration: int, requests_per_second: int
) -> None:
    """Run sustained load test."""
    print(f"\n🔥 Starting sustained test: {requests_per_second} req/s for {duration}s")

    async with httpx.AsyncClient(base_url=base_url) as client:
        start_time = time.time()
        end_time = start_time + duration
        request_count = 0
        success_count = 0
        response_times = []

        async def worker(worker_id: int):
            nonlocal request_count, success_count
            worker_request_count = 0

            while time.time() < end_time:
                status, elapsed = await simulate_voice_user(
                    client, f"{worker_id}-{worker_request_count}"
                )
                request_count += 1
                worker_request_count += 1
                
                if status == 200:
                    success_count += 1
                    response_times.append(elapsed)

                # Sleep to maintain target rate
                await asyncio.sleep(1.0 / requests_per_second)

        # Use multiple workers to achieve target rate
        num_workers = min(requests_per_second, 10)
        workers = [worker(i) for i in range(num_workers)]
        await asyncio.gather(*workers)

        # Calculate results
        actual_duration = time.time() - start_time
        actual_rate = request_count / actual_duration

        print(f"\n📊 Sustained test completed:")
        print(f"  Duration: {actual_duration:.1f}s")
        print(f"  Total requests: {request_count}")
        print(f"  Actual rate: {actual_rate:.1f} req/s")
        print(f"  Success rate: {(success_count / request_count * 100):.1f}%")

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"  Average response: {avg_time:.3f}s")


async def main():
    parser = argparse.ArgumentParser(description="Voice modality load testing")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--mode",
        choices=["concurrent", "sustained"],
        default="concurrent",
        help="Test mode (default: concurrent)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Number of concurrent users (default: 10)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations for concurrent test (default: 1)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration in seconds for sustained test (default: 30)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=10,
        help="Requests per second for sustained test (default: 10)",
    )

    args = parser.parse_args()

    # Set voice mode enabled
    os.environ["VOICE_MODE_ENABLED"] = "true"

    print("🎯 Voice Modality Load Testing")
    print(f"📍 Target: {args.url}")

    try:
        if args.mode == "concurrent":
            await run_concurrent_test(args.url, args.users, args.iterations)
        else:
            await run_sustained_test(args.url, args.duration, args.rate)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())