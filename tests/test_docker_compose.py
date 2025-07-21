#!/usr/bin/env python3
"""
Critical test for docker-compose functionality.
This script validates that docker-compose.dev.yml works correctly.
"""

import json
import subprocess
import sys
import time
import requests
import os


def run_command(cmd, timeout=120):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds")
        return 1, "", "Command timed out"


def test_docker_compose_build():
    """Test that docker-compose build succeeds."""
    print("\n=== Testing docker-compose build ===")

    code, stdout, stderr = run_command(
        "docker compose -f docker-compose.dev.yml build", timeout=240
    )

    if code != 0:
        print(f"❌ Docker compose build failed with code {code}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

    print("✅ Docker compose build succeeded")
    return True


def test_docker_compose_up():
    """Test that docker-compose up starts services correctly."""
    print("\n=== Testing docker-compose up ===")

    # Start services in detached mode
    code, stdout, stderr = run_command(
        "docker compose -f docker-compose.dev.yml up -d", timeout=120
    )

    if code != 0:
        print(f"❌ Docker compose up failed with code {code}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

    print("✅ Docker compose up succeeded")

    # Wait for services to start with optimized timing
    print("Waiting for services to initialize...")
    if not wait_for_service_health(max_wait_time=90, poll_interval=5):
        print("❌ Services failed to initialize within the expected time")
        return False

    # Check service health
    return check_service_health()


def wait_for_service_health(max_wait_time=60, poll_interval=5):
    """Wait for services to be healthy with efficient polling."""
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < max_wait_time:
        attempt += 1
        elapsed = time.time() - start_time
        print(f"Checking service health (attempt {attempt}, elapsed: {elapsed:.1f}s)...")
        
        # Check container health status using docker-compose ps with JSON format
        code, stdout, stderr = run_command(
            "docker compose -f docker-compose.dev.yml ps --format json", timeout=10
        )
        
        if code == 0 and stdout.strip():
            try:
                containers = []
                # Parse each line as a separate JSON object
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        containers.append(json.loads(line))
                
                # Check if backend container is healthy
                backend_healthy = False
                for container in containers:
                    if 'backend' in container.get('Service', '').lower():
                        state = container.get('State', '').lower()
                        health = container.get('Health', '').lower()
                        print(f"Backend container - State: {state}, Health: {health}")
                        
                        # Check if the container is running and explicitly healthy
                        if 'running' in state and ('healthy' in health):
                            backend_healthy = True
                            break
                        # Handle cases where health is empty (assumed healthy if running)
                        elif 'running' in state and health == '':
                            print("Warning: Health status is empty, assuming healthy.")
                            backend_healthy = True
                            break
                
                if backend_healthy:
                    print("✅ Backend container is healthy, proceeding with API health check...")
                    return True
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing container status: {e}")
        
        # If containers aren't ready yet, wait before next attempt
        if time.time() - start_time < max_wait_time:
            print(f"Services not ready yet, waiting {poll_interval}s before next check...")
            time.sleep(poll_interval)
    
    print(f"Services did not become healthy within {max_wait_time}s")
    return False


def check_service_health():
    """Check that all services are healthy."""
    print("\n=== Checking service health ===")

    # Check container status
    code, stdout, stderr = run_command("docker compose -f docker-compose.dev.yml ps")
    print(f"Container status:\n{stdout}")

    # Check backend health endpoint with efficient retries
    backend_healthy = False
    max_retries = 6  # 6 retries over 30 seconds
    retry_interval = 5
    
    for retry in range(max_retries):
        try:
            backend_host = os.getenv("BACKEND_HOST", "localhost")
            backend_port = os.getenv("BACKEND_PORT", "5001")
            backend_url = f"http://{backend_host}:{backend_port}/api/v1/health"
            print(f"Testing backend health endpoint (attempt {retry + 1}/{max_retries}): {backend_url}")
            
            response = requests.get(backend_url, timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check passed")
                backend_healthy = True
                break
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                print(f"Response content: {response.text}")
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
        
        if retry < max_retries - 1:
            print(f"Waiting {retry_interval}s before retry...")
            time.sleep(retry_interval)

    if not backend_healthy:
        print("❌ Backend health check failed after all retries")
        # Get final logs for debugging
        code, stdout, stderr = run_command(
            "docker compose -f docker-compose.dev.yml logs --tail=30 backend", timeout=30
        )
        print(f"Recent backend logs:\n{stdout}")
        return False

    # Quick frontend connection test (non-blocking)
    try:
        print("Testing frontend connection...")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost")
        frontend_port = os.getenv("FRONTEND_PORT", "3000")
        full_frontend_url = f"{frontend_url}:{frontend_port}"
        response = requests.get(full_frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend connection test passed")
        else:
            print(f"✅ Frontend responded with status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Frontend connection test failed (may be normal): {e}")

    return True


def cleanup():
    """Clean up docker containers and networks."""
    print("\n=== Cleaning up ===")
    run_command("docker compose -f docker-compose.dev.yml down --volumes --remove-orphans", timeout=60)
    print("✅ Cleanup completed")


def main():
    """Main test function."""
    print("🚀 Starting critical docker-compose test")

    success = True

    try:
        # Test build
        if not test_docker_compose_build():
            success = False

        # Test up and health checks
        if success and not test_docker_compose_up():
            success = False

    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Test failed with unexpected error: {e}")
        success = False
    finally:
        # Always cleanup
        cleanup()

    if success:
        print("\n🎉 All docker-compose tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Docker-compose tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
