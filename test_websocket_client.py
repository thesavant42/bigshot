#!/usr/bin/env python
"""
Simple WebSocket client to test real-time job updates
"""

import socketio
import time
import json

# Create a Socket.IO client
sio = socketio.Client()


# Event handlers
@sio.event
def connect():
    print("Connected to server")


@sio.event
def connected(data):
    print(f"Server says: {data}")


@sio.event
def job_update(data):
    print(f"Job update: {json.dumps(data, indent=2)}")


@sio.event
def active_jobs(data):
    print(f"Active jobs: {json.dumps(data, indent=2)}")


@sio.event
def subscribed(data):
    print(f"Subscribed: {data}")


@sio.event
def subscribed_all(data):
    print(f"Subscribed to all: {data}")


@sio.event
def error(data):
    print(f"Error: {data}")


@sio.event
def disconnect():
    print("Disconnected from server")


def test_websocket_connection():
    """Test WebSocket connection with authentication"""

    # You would need to get a real JWT token for authentication
    # For demo purposes, we'll use a placeholder
    auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY5ODEyNzIwMH0.example"

    try:
        # Connect with authentication
        sio.connect("http://localhost:5000", auth={"token": auth_token})

        # Subscribe to all job updates
        sio.emit("subscribe_all_jobs")

        # Get active jobs
        sio.emit("get_active_jobs")

        # Subscribe to specific job (if you have a job ID)
        # sio.emit('subscribe_job', {'job_id': 1})

        # Keep the connection alive
        print("WebSocket client running. Press Ctrl+C to stop.")
        sio.wait()

    except KeyboardInterrupt:
        print("Stopping WebSocket client...")
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_websocket_connection()
