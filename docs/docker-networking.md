# Docker Networking Configuration for BigShot

This document describes the proper configuration for frontend-backend communication in Docker deployments.

## Overview

BigShot uses a smart environment detection system that automatically configures API and WebSocket URLs based on the deployment environment:

- **Development (vite dev server)**: Uses relative URLs that are proxied by Vite
- **Production (Docker with nginx)**: Uses relative URLs that are proxied by nginx
- **Explicit URL override**: Allows manual configuration when needed

## Architecture

```
Frontend Container (nginx/vite) ←→ Backend Container (Flask)
        ↓                                    ↓
    Port 80/3000                        Port 5000
        ↓                                    ↓ 
   Service: frontend                Service: backend
```

## Configuration Files

### 1. Frontend Configuration (`src/config.ts`)

The frontend automatically detects the environment and configures URLs:

```typescript
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // Development: use relative URLs for Vite proxy
  if (import.meta.env.DEV) {
    return ""; // Vite proxy handles /api -> backend
  }
  
  // Production: use relative URLs for nginx proxy
  if (envUrl === "") {
    return ""; // nginx proxies to backend:5000
  }
  
  // Explicit override
  return envUrl || 'http://localhost:5000';
};
```

### 2. Vite Proxy Configuration (`vite.config.ts`)

For development, Vite proxies API calls to the backend:

```typescript
server: {
  port: 3000,
  host: '0.0.0.0', // Allow external connections in Docker
  proxy: {
    '/api': {
      target: process.env.VITE_API_URL || 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
    },
    '/socket.io': {
      target: process.env.VITE_API_URL || 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      ws: true,
    },
  },
}
```

### 3. Nginx Configuration (`nginx.conf`)

For production, nginx proxies requests to the backend:

```nginx
# API proxy to backend
location /api/ {
    proxy_pass http://backend:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# WebSocket proxy for Socket.IO
location /socket.io/ {
    proxy_pass http://backend:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # ... additional headers
}
```

## Docker Compose Configurations

### Development (`docker-compose.dev.yml`)

```yaml
services:
  backend:
    ports:
      - "5001:5000"  # Backend accessible on host:5001
    container_name: bigshot_dev_backend

  frontend:
    ports:
      - "3000:3000"  # Frontend accessible on host:3000
    environment:
      - VITE_API_URL=http://backend:5000  # Points to backend service
```

### Production (`docker-compose.yml`)

```yaml
services:
  backend:
    ports:
      - "127.0.0.1:5000:5000"  # Backend only accessible locally
    container_name: bigshot_backend

  frontend:
    ports:
      - "127.0.0.1:80:80"  # Frontend on port 80
    environment:
      - VITE_API_URL=""  # Use relative URLs for nginx proxy
```

## Troubleshooting

### Common Issues

1. **WebSocket connection failures to `ws://localhost:3000`**
   - **Cause**: Frontend trying to connect to wrong URL
   - **Solution**: Environment detection should use relative URLs in production

2. **422/500 errors on API endpoints**
   - **Cause**: API requests not being proxied correctly
   - **Solution**: Ensure nginx/Vite proxy configuration is correct

3. **"Failed to check service status" errors**
   - **Cause**: Backend not reachable from frontend container
   - **Solution**: Use Docker service names (e.g., `backend:5000`) in container-to-container communication

### Verification Steps

1. **Check environment detection**:
   ```bash
   # Should show correct API URLs based on environment
   node /tmp/test_environment_detection.js
   ```

2. **Verify Docker networking**:
   ```bash
   # List services
   docker compose config --services
   
   # Check container networking
   docker network ls
   ```

3. **Test API connectivity**:
   ```bash
   # From within frontend container
   curl http://backend:5000/api/v1/health
   
   # From host machine
   curl http://localhost/api/v1/health  # Production
   curl http://localhost:3000/api/v1/health  # Development
   ```

## Best Practices

1. **Use service names for container-to-container communication**
   - ✅ `backend:5000`
   - ❌ `localhost:5000`

2. **Use relative URLs in frontend when possible**
   - ✅ `/api/v1/endpoint`
   - ❌ `http://localhost:5000/api/v1/endpoint`

3. **Configure proxy servers properly**
   - Vite for development
   - nginx for production

4. **Set appropriate CORS headers in backend**
   - Allow requests from frontend service origin

5. **Use health checks to ensure services are ready**
   - Backend should be healthy before frontend starts

## Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `VITE_API_URL` | `http://backend:5000` | `""` | API base URL |
| `NODE_ENV` | `development` | `production` | Node environment |
| `FLASK_ENV` | `development` | `production` | Flask environment |

## Port Mapping

| Service | Container Port | Host Port (Dev) | Host Port (Prod) |
|---------|----------------|-----------------|------------------|
| Frontend | 3000 (vite) / 80 (nginx) | 3000 | 80 |
| Backend | 5000 | 5001 | 5000 (localhost only) |
| Database | 5432 | 5433 | 5432 (localhost only) |
| Redis | 6379 | 6380 | 6379 (localhost only) |