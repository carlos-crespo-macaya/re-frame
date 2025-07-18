#!/usr/bin/env python3
"""Analyze performance test results and generate report."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_metrics(metrics_file: str = "performance-metrics.json") -> dict:
    """Load performance metrics from file."""
    try:
        with open(metrics_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "uptime_seconds": 0,
            "total_requests": 0,
            "error_count": 0,
            "error_rate": 0,
            "throughput_rps": 0,
            "response_times": {},
            "audio_processing": {},
            "concurrent_sessions": {},
        }


def generate_markdown_report(metrics: dict) -> str:
    """Generate a markdown performance report."""
    report = []
    
    # Header
    report.append("# Voice Modality Performance Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n## Summary")
    
    # Overall metrics
    report.append(f"\n- **Total Requests**: {metrics.get('total_requests', 0):,}")
    report.append(f"- **Error Count**: {metrics.get('error_count', 0):,}")
    report.append(f"- **Error Rate**: {metrics.get('error_rate', 0):.2%}")
    report.append(f"- **Throughput**: {metrics.get('throughput_rps', 0):.1f} req/s")
    
    # Response times
    if "response_times" in metrics and metrics["response_times"]:
        rt = metrics["response_times"]
        report.append("\n## Response Times")
        report.append(f"- **Min**: {rt.get('min', 0):.3f}s")
        report.append(f"- **Average**: {rt.get('avg', 0):.3f}s")
        report.append(f"- **P50**: {rt.get('p50', 0):.3f}s")
        report.append(f"- **P95**: {rt.get('p95', 0):.3f}s")
        report.append(f"- **P99**: {rt.get('p99', 0):.3f}s")
        report.append(f"- **Max**: {rt.get('max', 0):.3f}s")
    
    # Audio processing breakdown
    if "audio_processing" in metrics and metrics["audio_processing"]:
        report.append("\n## Audio Processing Times")
        for stage, times in metrics["audio_processing"].items():
            report.append(f"\n### {stage.title()}")
            report.append(f"- **Average**: {times.get('avg', 0):.3f}s")
            report.append(f"- **Min**: {times.get('min', 0):.3f}s")
            report.append(f"- **Max**: {times.get('max', 0):.3f}s")
    
    # STT/TTS latencies
    if "stt_latency_avg" in metrics:
        report.append(f"\n## STT Latency: {metrics['stt_latency_avg']:.3f}s average")
    if "tts_latency_avg" in metrics:
        report.append(f"\n## TTS Latency: {metrics['tts_latency_avg']:.3f}s average")
    
    # Concurrent sessions
    if "concurrent_sessions" in metrics and metrics["concurrent_sessions"]:
        cs = metrics["concurrent_sessions"]
        report.append("\n## Concurrent Sessions")
        report.append(f"- **Max**: {cs.get('max', 0)}")
        report.append(f"- **Average**: {cs.get('avg', 0):.1f}")
    
    # Performance assessment
    report.append("\n## Performance Assessment")
    
    # Check if performance meets targets
    issues = []
    
    if metrics.get("error_rate", 0) > 0.01:
        issues.append("❌ Error rate exceeds 1% threshold")
    else:
        report.append("✅ Error rate within acceptable limits")
    
    rt = metrics.get("response_times", {})
    if rt.get("p95", 0) > 2.0:
        issues.append(f"❌ P95 response time ({rt['p95']:.2f}s) exceeds 2s target")
    else:
        report.append("✅ P95 response time meets target")
    
    if rt.get("p99", 0) > 5.0:
        issues.append(f"❌ P99 response time ({rt['p99']:.2f}s) exceeds 5s target")
    else:
        report.append("✅ P99 response time meets target")
    
    if metrics.get("throughput_rps", 0) < 10:
        issues.append(f"❌ Throughput ({metrics['throughput_rps']:.1f} req/s) below 10 req/s target")
    else:
        report.append("✅ Throughput meets minimum target")
    
    # Report issues
    if issues:
        report.append("\n### ⚠️ Performance Issues Detected")
        for issue in issues:
            report.append(f"- {issue}")
    else:
        report.append("\n### 🎉 All Performance Targets Met!")
    
    # Recommendations
    if issues:
        report.append("\n## Recommendations")
        if metrics.get("error_rate", 0) > 0.01:
            report.append("- Investigate error logs to identify root causes")
            report.append("- Consider implementing retry mechanisms")
        
        if rt.get("p95", 0) > 2.0 or rt.get("p99", 0) > 5.0:
            report.append("- Profile slow requests to identify bottlenecks")
            report.append("- Consider caching frequently accessed data")
            report.append("- Optimize audio processing pipeline")
        
        if metrics.get("throughput_rps", 0) < 10:
            report.append("- Scale up backend resources")
            report.append("- Implement request queuing and batching")
    
    return "\n".join(report)


def main():
    """Main entry point."""
    # Check if running in CI environment
    is_ci = os.getenv("CI", "false").lower() == "true"
    
    # Try to fetch metrics from API if available
    if not is_ci:
        try:
            import requests
            response = requests.get("http://localhost:8000/api/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                # Save metrics for future reference
                with open("performance-metrics.json", "w") as f:
                    json.dump(metrics, f, indent=2)
            else:
                metrics = load_metrics()
        except Exception:
            metrics = load_metrics()
    else:
        metrics = load_metrics()
    
    # Generate report
    report = generate_markdown_report(metrics)
    
    # Output report
    print(report)
    
    # Save report to file
    with open("performance-report.md", "w") as f:
        f.write(report)
    
    # Exit with error if performance issues detected
    if metrics.get("error_rate", 0) > 0.01 or \
       metrics.get("response_times", {}).get("p95", 0) > 2.0 or \
       metrics.get("response_times", {}).get("p99", 0) > 5.0 or \
       metrics.get("throughput_rps", 0) < 10:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()