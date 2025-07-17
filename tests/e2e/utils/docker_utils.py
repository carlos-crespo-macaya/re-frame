"""
Docker utilities for E2E tests.
"""
import subprocess
import time
import requests
from typing import List, Dict, Optional


class DockerComposeManager:
    """Manages Docker Compose services for tests."""
    
    def __init__(self, compose_files: List[str], project_name: str = "re-frame-test"):
        self.compose_files = compose_files
        self.project_name = project_name
        self.base_cmd = ["docker-compose", "-p", project_name]
        
        # Add all compose files to base command
        for file in compose_files:
            self.base_cmd.extend(["-f", file])
    
    def up(self, services: Optional[List[str]] = None, detached: bool = True) -> bool:
        """Start Docker Compose services."""
        cmd = self.base_cmd + ["up"]
        if detached:
            cmd.append("-d")
        if services:
            cmd.extend(services)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Docker Compose up: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start services: {e.stderr}")
            return False
    
    def down(self, volumes: bool = False) -> bool:
        """Stop Docker Compose services."""
        cmd = self.base_cmd + ["down"]
        if volumes:
            cmd.append("-v")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Docker Compose down: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop services: {e.stderr}")
            return False
    
    def logs(self, service: Optional[str] = None, tail: int = 100) -> str:
        """Get logs from services."""
        cmd = self.base_cmd + ["logs", f"--tail={tail}"]
        if service:
            cmd.append(service)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Failed to get logs: {e.stderr}"
    
    def ps(self) -> List[Dict[str, str]]:
        """List running services."""
        cmd = self.base_cmd + ["ps", "--format", "json"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Parse JSON output if available
            return []  # Simplified for now
        except subprocess.CalledProcessError:
            return []
    
    def wait_for_healthy(self, services: Dict[str, str], timeout: int = 60) -> bool:
        """
        Wait for services to be healthy.
        
        Args:
            services: Dict of service_name -> health_check_url
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service, url in services.items():
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code != 200:
                        print(f"{service} not healthy yet (status: {response.status_code})")
                        all_healthy = False
                        break
                except requests.exceptions.RequestException as e:
                    print(f"{service} not reachable: {e}")
                    all_healthy = False
                    break
            
            if all_healthy:
                print("All services are healthy!")
                return True
            
            time.sleep(2)
        
        # Print final service status
        print("\nService health check timeout. Final status:")
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=2)
                print(f"  {service}: {response.status_code}")
            except Exception as e:
                print(f"  {service}: {type(e).__name__}")
        
        return False
    
    def exec(self, service: str, command: List[str]) -> str:
        """Execute a command in a running service."""
        cmd = self.base_cmd + ["exec", "-T", service] + command
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Command failed: {e.stderr}"