"""
WebSocket service for real-time job updates
"""

import json
import redis
import threading
import time
import logging
from datetime import datetime, UTC
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from config.config import Config


class WebSocketService:
    """Service for managing WebSocket connections and real-time updates"""

    def __init__(self, app=None):
        self.socketio = None
        self.redis_client = None
        self.pubsub_thread = None
        self.active_connections = {}
        self.redis_available = False
        self.redis_retry_count = 0
        self.max_redis_retries = 5
        self.logger = logging.getLogger('bigshot.websocket')

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize WebSocket service with Flask app"""

        # Initialize SocketIO
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode="eventlet",
        )

        # Initialize Redis client with error handling
        self._initialize_redis()

        # Set up event handlers
        self._setup_event_handlers()

        # Start Redis pubsub listener (only if Redis is available)
        if self.redis_available:
            self._start_pubsub_listener()
        else:
            self.logger.warning(
                "WebSocket service starting without Redis pub/sub capabilities"
            )

    def _initialize_redis(self):
        """Initialize Redis client with error handling and retry logic"""
        try:
            self.redis_client = redis.Redis.from_url(Config.REDIS_URL)
            # Test the connection
            self.redis_client.ping()
            self.redis_available = True
            self.redis_retry_count = 0
            self.logger.info("Redis connection established successfully for WebSocket service")
        except redis.ConnectionError as e:
            self.redis_available = False
            self.logger.warning(
                f"Redis connection failed: {e}. WebSocket will work without pub/sub features."
            )
        except Exception as e:
            self.redis_available = False
            self.logger.error(f"Unexpected error connecting to Redis: {e}")

    def _retry_redis_connection(self):
        """Retry Redis connection with exponential backoff"""
        if self.redis_retry_count >= self.max_redis_retries:
            self.logger.error(
                f"Maximum Redis retry attempts ({self.max_redis_retries}) reached. Giving up."
            )
            return False

        self.redis_retry_count += 1
        wait_time = min(2 ** self.redis_retry_count, 60)  # Exponential backoff, max 60 seconds

        self.logger.info(
            f"Attempting Redis reconnection #{self.redis_retry_count} in {wait_time} seconds..."
        )
        time.sleep(wait_time)

        self._initialize_redis()
        return self.redis_available

    def _setup_event_handlers(self):
        """Set up WebSocket event handlers"""

        @self.socketio.on("connect")
        def handle_connect(auth):
            """Handle client connection"""
            try:
                # Verify JWT token
                token = auth.get("token") if auth else None
                if not token:
                    return False

                # Decode token to get user info
                decoded_token = decode_token(token)
                user_id = decoded_token.get("sub")

                if not user_id:
                    return False

                # Store connection info
                self.active_connections[request.sid] = {
                    "user_id": user_id,
                    "connected_at": datetime.now(UTC).isoformat(),
                    "subscriptions": set(),
                }

                print(f"Client {request.sid} connected for user {user_id}")

                # Send welcome message with Redis status
                emit(
                    "connected",
                    {
                        "message": "Connected to bigshot job updates",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "pubsub_available": self.redis_available,
                    },
                )

                return True

            except Exception as e:
                print(f"Connection error: {e}")
                self.logger.error(f"WebSocket connection error: {e}")
                return False

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection"""
            if request.sid in self.active_connections:
                user_id = self.active_connections[request.sid]["user_id"]
                del self.active_connections[request.sid]
                print(f"Client {request.sid} disconnected for user {user_id}")

        @self.socketio.on("subscribe_job")
        def handle_subscribe_job(data):
            """Handle job subscription"""
            try:
                job_id = data.get("job_id")
                if not job_id:
                    emit("error", {"message": "job_id required"})
                    return

                # Join room for this job
                room = f"job_{job_id}"
                join_room(room)

                # Add to subscriptions
                if request.sid in self.active_connections:
                    self.active_connections[request.sid]["subscriptions"].add(job_id)

                emit(
                    "subscribed",
                    {
                        "job_id": job_id,
                        "message": f"Subscribed to job {job_id} updates",
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

                print(f"Client {request.sid} subscribed to job {job_id}")

            except Exception as e:
                emit("error", {"message": str(e)})

        @self.socketio.on("unsubscribe_job")
        def handle_unsubscribe_job(data):
            """Handle job unsubscription"""
            try:
                job_id = data.get("job_id")
                if not job_id:
                    emit("error", {"message": "job_id required"})
                    return

                # Leave room for this job
                room = f"job_{job_id}"
                leave_room(room)

                # Remove from subscriptions
                if request.sid in self.active_connections:
                    self.active_connections[request.sid]["subscriptions"].discard(
                        job_id
                    )

                emit(
                    "unsubscribed",
                    {
                        "job_id": job_id,
                        "message": f"Unsubscribed from job {job_id} updates",
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

                print(f"Client {request.sid} unsubscribed from job {job_id}")

            except Exception as e:
                emit("error", {"message": str(e)})

        @self.socketio.on("subscribe_all_jobs")
        def handle_subscribe_all_jobs():
            """Handle subscription to all job updates"""
            try:
                # Join general updates room
                join_room("all_jobs")

                emit(
                    "subscribed_all",
                    {
                        "message": "Subscribed to all job updates",
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

                print(f"Client {request.sid} subscribed to all job updates")

            except Exception as e:
                emit("error", {"message": str(e)})

        @self.socketio.on("get_active_jobs")
        def handle_get_active_jobs():
            """Handle request for active jobs"""
            try:
                from app.models.models import Job

                # Get active jobs (pending or running)
                active_jobs = Job.query.filter(
                    Job.status.in_(["pending", "running"])
                ).all()

                jobs_data = []
                for job in active_jobs:
                    jobs_data.append(
                        {
                            "id": job.id,
                            "type": job.type,
                            "domain": job.domain,
                            "status": job.status,
                            "progress": job.progress,
                            "created_at": (
                                job.created_at.isoformat() if job.created_at else None
                            ),
                            "updated_at": (
                                job.updated_at.isoformat() if job.updated_at else None
                            ),
                        }
                    )

                emit(
                    "active_jobs",
                    {
                        "jobs": jobs_data,
                        "count": len(jobs_data),
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

            except Exception as e:
                emit("error", {"message": str(e)})

    def _start_pubsub_listener(self):
        """Start Redis pubsub listener in background thread"""

        def pubsub_listener():
            """Listen for Redis pubsub messages and broadcast to WebSocket clients"""
            while True:
                try:
                    if not self.redis_available:
                        self.logger.info("Attempting to reconnect to Redis for pubsub...")
                        if not self._retry_redis_connection():
                            self.logger.error(
                                "Failed to reconnect to Redis. Retrying in 30 seconds..."
                            )
                            time.sleep(30)
                            continue

                    pubsub = self.redis_client.pubsub()
                    pubsub.subscribe(["job_updates"])

                    self.logger.info("Started Redis pubsub listener for job updates")

                    for message in pubsub.listen():
                        if message["type"] == "message":
                            try:
                                # Parse job update data
                                data = json.loads(message["data"])
                                job_id = data.get("job_id")
                                update_type = data.get("update_type")

                                if job_id and update_type:
                                    # Broadcast to specific job room
                                    self.socketio.emit(
                                        "job_update", data, room=f"job_{job_id}"
                                    )

                                    # Broadcast to all jobs room
                                    self.socketio.emit("job_update", data, room="all_jobs")

                                    print(
                                        f"Broadcasted {update_type} update for job {job_id}"
                                    )

                            except json.JSONDecodeError:
                                self.logger.warning(
                                    f"Invalid JSON in pubsub message: {message['data']}"
                                )
                            except Exception as e:
                                self.logger.error(f"Error processing pubsub message: {e}")

                except redis.ConnectionError as e:
                    self.redis_available = False
                    self.logger.error(f"Redis connection lost in pubsub listener: {e}")
                    # Close the pubsub connection if it exists
                    try:
                        pubsub.close()
                    except Exception:
                        pass
                    # Wait before retrying
                    time.sleep(5)
                    continue

                except Exception as e:
                    self.logger.error(f"Unexpected error in pubsub listener: {e}")
                    time.sleep(10)  # Wait before retrying on unexpected errors
                    continue

        # Start listener in background thread
        self.pubsub_thread = threading.Thread(target=pubsub_listener)
        self.pubsub_thread.daemon = True
        self.pubsub_thread.start()

    def broadcast_job_update(self, job_id, update_type, data=None):
        """Broadcast job update to WebSocket clients"""
        try:
            # Prepare broadcast data
            broadcast_data = {
                "job_id": job_id,
                "update_type": update_type,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            if data:
                broadcast_data.update(data)

            # If Redis is available, publish to Redis for pubsub listener
            if self.redis_available:
                try:
                    self.redis_client.publish("job_updates", json.dumps(broadcast_data))
                except redis.ConnectionError:
                    self.redis_available = False
                    self.logger.warning(
                        "Redis connection lost during broadcast. Falling back to direct emit."
                    )
                    # Fall through to direct emit
                except Exception as e:
                    self.logger.error(f"Error publishing to Redis: {e}")
                    # Fall through to direct emit

            # If Redis is not available, emit directly to connected clients
            if not self.redis_available:
                self.logger.debug(
                    f"Broadcasting job update directly (Redis unavailable): "
                    f"{update_type} for job {job_id}"
                )
                # Broadcast to specific job room
                self.socketio.emit("job_update", broadcast_data, room=f"job_{job_id}")
                # Broadcast to all jobs room
                self.socketio.emit("job_update", broadcast_data, room="all_jobs")

        except Exception as e:
            self.logger.error(f"Error broadcasting job update: {e}")

    def get_connection_stats(self):
        """Get WebSocket connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "redis_available": self.redis_available,
            "redis_retry_count": self.redis_retry_count,
            "connections": [
                {
                    "sid": sid,
                    "user_id": conn["user_id"],
                    "connected_at": conn["connected_at"],
                    "subscriptions": list(conn["subscriptions"]),
                }
                for sid, conn in self.active_connections.items()
            ],
        }

    def get_stats(self):
        """Alias for get_connection_stats for backward compatibility"""
        return self.get_connection_stats()


# Global WebSocket service instance
websocket_service = WebSocketService()
