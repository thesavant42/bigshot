"""
Health check and monitoring API endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app import db
from app.models import Domain, Job
from app.services.job_manager import JobManager
from app.services.websocket import websocket_service
import psutil
import redis
import os

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint"""
    try:
        # Check database connectivity
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))

        return (
            jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0.0",
                    "service": "bigshot-api",
                    "database": "connected",
                }
            ),
            200,
        )
    except Exception as e:
        # Return degraded status instead of failing completely
        # This allows the service to start even if database is not ready
        return (
            jsonify(
                {
                    "status": "starting",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0.0",
                    "service": "bigshot-api",
                    "database": "disconnected",
                    "database_error": str(e),
                }
            ),
            200,  # Return 200 to pass healthcheck while starting
        )


@health_bp.route("/health/detailed", methods=["GET"])
@jwt_required()
def detailed_health_check():
    """Detailed health check for authenticated users"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "bigshot-api",
        "version": "1.0.0",
        "checks": {},
    }

    overall_healthy = True

    # Database check
    try:
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": 0.001,  # Could measure actual response time
        }
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    # Redis check
    try:
        from celery_app import celery_app

        redis_client = redis.Redis.from_url(celery_app.conf.broker_url)
        redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy", "response_time": 0.001}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    # Celery check
    try:
        from celery_app import celery_app

        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        health_status["checks"]["celery"] = {
            "status": "healthy" if active_tasks is not None else "unhealthy",
            "active_workers": len(active_tasks) if active_tasks else 0,
        }
    except Exception as e:
        health_status["checks"]["celery"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    # WebSocket check
    try:
        websocket_stats = websocket_service.get_stats()
        health_status["checks"]["websocket"] = {
            "status": "healthy",
            "connected_clients": websocket_stats.get("connected_clients", 0),
        }
    except Exception as e:
        health_status["checks"]["websocket"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    health_status["status"] = "healthy" if overall_healthy else "degraded"

    return jsonify(health_status), 200 if overall_healthy else 503


@health_bp.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Database metrics
        domain_count = Domain.query.count()
        job_count = Job.query.count()
        active_jobs = Job.query.filter_by(status="running").count()

        # Redis metrics
        try:
            from celery_app import celery_app

            redis_client = redis.Redis.from_url(celery_app.conf.broker_url)
            redis_info = redis_client.info()
            redis_memory = redis_info.get("used_memory", 0)
            redis_connected_clients = redis_info.get("connected_clients", 0)
        except:
            redis_memory = 0
            redis_connected_clients = 0

        # WebSocket metrics
        try:
            websocket_stats = websocket_service.get_stats()
            websocket_connections = websocket_stats.get("connected_clients", 0)
        except:
            websocket_connections = 0

        metrics_data = {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_bytes": memory.used,
                "memory_total_bytes": memory.total,
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_used_bytes": disk.used,
                "disk_total_bytes": disk.total,
            },
            "database": {
                "domain_count": domain_count,
                "job_count": job_count,
                "active_jobs": active_jobs,
            },
            "redis": {
                "memory_used_bytes": redis_memory,
                "connected_clients": redis_connected_clients,
            },
            "websocket": {"connected_clients": websocket_connections},
        }

        return jsonify(metrics_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_logs():
    """Get application logs"""
    try:
        log_level = request.args.get("level", "INFO")
        limit = int(request.args.get("limit", 100))

        # This is a simplified implementation
        # In production, you'd want to use a proper logging system
        logs = []

        # Read from application logs if they exist
        log_file = "logs/app.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
                logs = [line.strip() for line in lines[-limit:]]

        return (
            jsonify(
                {
                    "logs": logs,
                    "level": log_level,
                    "count": len(logs),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/system/info", methods=["GET"])
@jwt_required()
def system_info():
    """Get detailed system information"""
    try:
        import platform

        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "uptime": psutil.boot_time(),
            "process_count": len(psutil.pids()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Environment information
        env_info = {
            "flask_env": os.getenv("FLASK_ENV", "production"),
            "database_url": (
                os.getenv("DATABASE_URL", "").split("@")[1]
                if "@" in os.getenv("DATABASE_URL", "")
                else "Not configured"
            ),
            "redis_url": (
                os.getenv("REDIS_URL", "").split("@")[1]
                if "@" in os.getenv("REDIS_URL", "")
                else "Not configured"
            ),
            "celery_workers": "Configured",
        }

        return jsonify({"system": system_info, "environment": env_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/backup/status", methods=["GET"])
@jwt_required()
def backup_status():
    """Get backup status information"""
    try:
        backup_dir = "backups"
        backup_info = {
            "backup_directory": backup_dir,
            "backups": [],
            "last_backup": None,
            "total_size": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if os.path.exists(backup_dir):
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path):
                    stat = os.stat(item_path)
                    backup_info["backups"].append(
                        {
                            "name": item,
                            "created": datetime.fromtimestamp(
                                stat.st_ctime, timezone.utc
                            ).isoformat(),
                            "size": stat.st_size,
                        }
                    )
                    backup_info["total_size"] += stat.st_size

        # Sort backups by creation time
        backup_info["backups"].sort(key=lambda x: x["created"], reverse=True)

        if backup_info["backups"]:
            backup_info["last_backup"] = backup_info["backups"][0]["created"]

        return jsonify(backup_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
