"""Tests for Docker build process."""

import os
import subprocess
import time


def test_dockerfile_exists():
    """Test that Dockerfile exists in the backend directory."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile should exist"


def test_dockerfile_has_health_check():
    """Test that Dockerfile includes HEALTHCHECK instruction."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    with open(dockerfile_path) as f:
        content = f.read()
    assert "HEALTHCHECK" in content, "Dockerfile should include HEALTHCHECK"


def test_dockerfile_uses_python_312():
    """Test that Dockerfile uses Python 3.12 slim image."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    with open(dockerfile_path) as f:
        content = f.read()
    assert "python:3.12-slim" in content, "Dockerfile should use python:3.12-slim"


def test_dockerfile_is_multistage():
    """Test that Dockerfile uses multi-stage build."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    with open(dockerfile_path) as f:
        content = f.read()
    # Check for multiple FROM statements indicating multi-stage
    from_count = content.count("FROM")
    assert from_count >= 2, "Dockerfile should use multi-stage build (at least 2 FROM statements)"


def test_dockerfile_sets_port_env():
    """Test that Dockerfile sets PORT environment variable."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    with open(dockerfile_path) as f:
        content = f.read()
    assert "ENV PORT" in content or "EXPOSE" in content, "Dockerfile should set PORT for Cloud Run"


def test_dockerfile_runs_as_nonroot():
    """Test that Dockerfile creates and uses non-root user."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
    with open(dockerfile_path) as f:
        content = f.read()
    assert "USER" in content, "Dockerfile should run as non-root user"
    assert "useradd" in content or "adduser" in content, "Dockerfile should create a user"


def test_docker_build_succeeds():
    """Test that Docker image builds successfully."""
    # Skip if Docker is not available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        import pytest

        pytest.skip("Docker not available")

    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        ["docker", "build", "-t", "re-frame-test:latest", "."],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Docker build failed: {result.stderr}"


def test_docker_image_size_reasonable():
    """Test that final Docker image is reasonably sized (< 1GB)."""
    # Skip if Docker is not available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        import pytest

        pytest.skip("Docker not available")

    # Get image size
    result = subprocess.run(
        ["docker", "images", "re-frame-test", "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        # Parse size (format: "123MB" or "1.23GB")
        size_str = result.stdout.strip()
        if "GB" in size_str:
            size_mb = float(size_str.replace("GB", "")) * 1024
        else:
            size_mb = float(size_str.replace("MB", ""))

        assert size_mb < 1024, f"Docker image too large: {size_mb}MB (should be < 1GB)"


def test_docker_container_health_check():
    """Test that container responds to health checks."""
    # Skip if Docker is not available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        import pytest

        pytest.skip("Docker not available")

    container_name = "re-frame-test-container"

    # Start container
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            "8000:8000",
            "-e",
            "GOOGLE_API_KEY=test-key",
            "re-frame-test:latest",
        ],
        capture_output=True,
    )

    try:
        # Wait for container to be healthy
        max_attempts = 30
        for i in range(max_attempts):
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
                capture_output=True,
                text=True,
            )

            if result.stdout.strip() == "healthy":
                break

            time.sleep(1)
        else:
            assert False, "Container did not become healthy in time"

        # Test health endpoint
        import requests

        response = requests.get("http://localhost:8000/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    finally:
        # Cleanup
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm", container_name], capture_output=True)
