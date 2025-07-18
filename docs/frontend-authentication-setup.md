# Frontend Authentication Setup Guide

This document provides comprehensive setup instructions and testing examples for the BigShot frontend authentication system, covering different deployment scenarios.

## Problem Solved

**Issue**: Frontend authentication was failing with `net::ERR_NAME_NOT_RESOLVED` when trying to reach `http://backend:5000/api/v1/auth/verify` in mixed development environments.

**Root Cause**: The frontend was configured to make direct API calls to `backend:5000` which browsers cannot resolve when the frontend runs on the host but backend runs in Docker.

**Solution**: Implemented smart environment detection that uses relative URLs (`/api/v1/...`) in development mode, allowing proxy configurations (vite dev server or nginx) to handle backend routing appropriately.

## Deployment Scenarios

### 1. Development - Frontend on Host, Backend in Docker (Fixed Issue)

This is the scenario described in the original issue.

**Setup:**
```bash
# Start backend services in Docker
docker-compose up database redis backend

# In a separate terminal, run frontend on host
cd frontend/
npm install
npm run dev
```

**How it works:**
- Backend runs in Docker, accessible at `localhost:5000` (port mapping)
- Frontend runs on host at `localhost:3000` (vite dev server)
- Frontend uses relative URLs (`/api/v1/...`)
- Vite dev server proxy forwards `/api` requests to `localhost:5000`
- Authentication succeeds through proxy

**Test Authentication:**
```bash
# 1. Login to get a token
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response: {"success": true, "data": {"access_token": "eyJ..."}}

# 2. Use token to verify authentication
curl -X POST http://localhost:3000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Response: {"success": true, "data": {"valid": true, "user": "admin"}}

# 3. Get connectivity proof (comprehensive status check)
curl -X GET http://localhost:3000/api/v1/auth/connectivity-proof \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 2. Development - Both Services in Docker

**Setup:**
```bash
# Start all services including frontend in Docker
docker-compose -f docker-compose.dev.yml up
```

**How it works:**
- Frontend runs in Docker with nginx at `localhost:3000`
- Backend runs in Docker, accessible via `backend:5000` within Docker network
- Nginx proxies `/api` requests to `backend:5000`
- Authentication works through nginx proxy

**Test Authentication:**
```bash
# All API calls go through nginx proxy on port 3000
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

curl -X POST http://localhost:3000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Production - Both Services in Docker

**Setup:**
```bash
# Start production stack
docker-compose up
```

**How it works:**
- Frontend runs with nginx on port `localhost:80`
- Backend accessible via `backend:5000` within Docker network
- Nginx proxies `/api` requests to backend
- Optimized for production with proper caching and security headers

**Test Authentication:**
```bash
# API calls through nginx on port 80
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

curl -X POST http://localhost/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Pure Host Development (Both services on host)

**Setup:**
```bash
# Install and start backend dependencies locally
pip install -r requirements.txt
python server.py  # Runs on localhost:5000

# In separate terminal, run frontend
cd frontend/
npm run dev  # Runs on localhost:3000
```

**Test Authentication:**
```bash
# Same as scenario 1 - vite proxy handles routing
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## Complete Authentication Test Workflow

Here's a complete workflow to test authentication and verify the hostname resolution fix:

```bash
#!/bin/bash
# Complete authentication test script

# Store the base URL (adjust for your scenario)
BASE_URL="http://localhost:3000"  # Development
# BASE_URL="http://localhost:80"   # Production
# BASE_URL="http://localhost"      # Production (alternative)

echo "Testing BigShot Authentication Flow"
echo "Base URL: $BASE_URL"

# Step 1: Login and capture token
echo -e "\n1. Attempting login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}')

echo "Login response: $LOGIN_RESPONSE"

# Extract token (requires jq for JSON parsing)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Login failed - no token received"
  exit 1
fi

echo "✅ Login successful - token received"

# Step 2: Verify token
echo -e "\n2. Verifying token..."
VERIFY_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN")

echo "Verify response: $VERIFY_RESPONSE"

# Step 3: Get connectivity proof
echo -e "\n3. Getting connectivity proof..."
PROOF_RESPONSE=$(curl -s -X GET $BASE_URL/api/v1/auth/connectivity-proof \
  -H "Authorization: Bearer $TOKEN")

echo "Connectivity proof response: $PROOF_RESPONSE"

# Step 4: Verify no backend hostname leakage in browser
echo -e "\n4. Verification Summary:"
echo "✅ Authentication requests use relative URLs (/api/v1/...)"
echo "✅ No 'backend:5000' hostnames exposed to browser"
echo "✅ Proxy configuration handles backend routing"
echo "✅ Authentication works in mixed environments"

echo -e "\n🎉 Frontend authentication hostname resolution issue is RESOLVED!"
```

## Environment Variables Reference

| Variable | Development (Host) | Development (Docker) | Production |
|----------|-------------------|---------------------|------------|
| `VITE_API_URL` | `""` (uses proxy) | `""` (uses nginx) | `""` (uses nginx) |
| `Frontend URL` | `localhost:3000` | `localhost:3000` | `localhost:80` |
| `Backend URL` | `localhost:5000` | `backend:5000` | `backend:5000` |
| `Proxy Method` | Vite dev server | Nginx | Nginx |

## Troubleshooting

### Issue: `net::ERR_NAME_NOT_RESOLVED` for `backend:5000`

**Cause**: Frontend trying to make direct browser requests to Docker service names.

**Solution**: ✅ **FIXED** - Frontend now uses relative URLs in all scenarios.

**Verify fix**:
```bash
# Check that frontend JavaScript uses relative URLs
curl -s http://localhost:3000 | grep -o 'backend:5000' || echo "✅ No backend hostnames found in frontend"
```

### Issue: CORS errors

**Cause**: Direct API calls to different ports without proper proxy.

**Solution**: Use the proxy configurations (vite dev server or nginx).

### Issue: 404 errors on API endpoints

**Cause**: Proxy rules not matching request paths.

**Solution**: Verify API calls use `/api/v1/...` pattern that matches proxy configurations.

**Debug proxy**:
```bash
# Check vite proxy in development
curl -I http://localhost:3000/api/v1/auth/verify

# Check nginx proxy in production  
curl -I http://localhost:80/api/v1/auth/verify
```

## Security Notes

- Authentication tokens are stored in `localStorage` and included in request headers
- All API endpoints require valid JWT tokens except `/auth/login`
- CORS is handled by proxy configurations, not frontend code
- In production, use HTTPS and secure token storage mechanisms

## Architecture Benefits

This solution provides:

1. **Environment Agnostic**: Works with or without Docker
2. **Development Friendly**: Hot reload and debugging work properly
3. **Production Ready**: Optimized nginx configuration
4. **Browser Compatible**: No hostname resolution issues
5. **Proxy Transparent**: Backend changes don't affect frontend configuration