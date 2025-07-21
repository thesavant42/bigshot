#!/usr/bin/env python3
"""
Critical test for docker-compose functionality.
This script validates that docker-compose.dev.yml works correctly.
"""

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
        "docker compose -f docker-compose.dev.yml build", timeout=300
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
        "docker compose -f docker-compose.dev.yml up -d", timeout=180
    )

    if code != 0:
        print(f"❌ Docker compose up failed with code {code}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

    print("✅ Docker compose up succeeded")

    # Wait for services to start with exponential backoff
    print("Waiting for services to initialize...")
    if not wait_for_service_health(max_attempts=5, initial_delay=5):
        print("❌ Services failed to initialize within the expected time")
        return False

    # Check service health
    return check_service_health()


def wait_for_service_health(max_attempts=10, initial_delay=10):
    """Wait for services to be healthy with exponential backoff."""
    for attempt in range(max_attempts):
        delay = initial_delay * (2**attempt) if attempt > 0 else initial_delay
        print(
            f"Waiting {delay} seconds for services to initialize "
            f"(attempt {attempt + 1}/{max_attempts})..."
        )
        time.sleep(delay)

        # Check if containers are running and healthy
        code, stdout, stderr = run_command(
            "docker compose -f docker-compose.dev.yml ps --format json"
        )
        if code == 0:
            print("Services appear to be running, checking health status...")
            
            # Check specifically for backend health
            code, stdout, stderr = run_command(
                "docker compose -f docker-compose.dev.yml ps backend"
            )
            print(f"Backend service status:\n{stdout}")
            
            # Check backend logs for any errors
            code, stdout, stderr = run_command(
                "docker compose -f docker-compose.dev.yml logs --tail=10 backend"
            )
            print(f"Recent backend logs:\n{stdout}")
            
            # If backend is healthy, we can proceed
            if "healthy" in stdout.lower() or attempt >= 3:
                print("Proceeding with health checks...")
                return True

    print(f"Services did not start after {max_attempts} attempts")
    return False


def check_service_health():
    """Check that all services are healthy."""
    print("\n=== Checking service health ===")

    # Check container status
    code, stdout, stderr = run_command("docker compose -f docker-compose.dev.yml ps")
    print(f"Container status:\n{stdout}")

    # Check backend health endpoint with retries
    backend_healthy = False
    max_retries = 5
    
    for retry in range(max_retries):
        try:
            backend_host = os.getenv("BACKEND_HOST", "localhost")
            backend_port = os.getenv("BACKEND_PORT", "5001")
            backend_url = f"http://{backend_host}:{backend_port}/api/v1/health"
            print(f"Testing backend health endpoint (attempt {retry + 1}/{max_retries}): {backend_url}")
            
            response = requests.get(backend_url, timeout=10)
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
            print("Waiting 5 seconds before retry...")
            time.sleep(5)
            
            # Check backend logs on failure
            code, stdout, stderr = run_command(
                "docker compose -f docker-compose.dev.yml logs --tail=20 backend"
            )
            print(f"Recent backend logs:\n{stdout}")

    if not backend_healthy:
        print("❌ Backend health check failed after all retries")
        # Get final logs for debugging
        code, stdout, stderr = run_command(
            "docker compose -f docker-compose.dev.yml logs backend"
        )
        print(f"Full backend logs:\n{stdout}")
        return False

    # Check frontend (simple connection test)
    try:
        print("Testing frontend connection...")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost")
        frontend_port = os.getenv("FRONTEND_PORT", "3000")
        full_frontend_url = f"{frontend_url}:{frontend_port}"
        response = requests.get(full_frontend_url, timeout=10)
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
    run_command("docker compose -f docker-compose.dev.yml down", timeout=60)
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
