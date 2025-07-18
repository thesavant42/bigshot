# WebSocket Eventlet Server Configuration Fix

## Issue Description

Users were experiencing WebSocket connection failures after authentication, with the following symptoms:

- Black screen after authentication with occasional flickering 
- Backend logs showing `RuntimeError: You need to use the eventlet server`
- WebSocket upgrade attempts failing with eventlet driver errors

## Root Cause

The WebSocket service was configured to use `async_mode="eventlet"` but the development Docker environment was running the backend with `python server.py`, which uses Flask's standard `app.run()` method instead of SocketIO's `socketio.run()` method required for eventlet.

## Solution

Changed the Docker development command in `docker-compose.dev.yml` from:
```yaml
command: python server.py
```

To:
```yaml  
command: python run.py
```

This ensures the development environment uses `app.socketio.run()` which properly initializes the eventlet server for WebSocket support.

## Verification

The fix has been validated with:

1. **Automated Tests**: Added comprehensive test suite covering WebSocket configuration
2. **Server Startup**: Confirmed server logs show "Server initialized for eventlet"
3. **WebSocket Operations**: Verified broadcast operations complete without eventlet errors
4. **HTTP Functionality**: Confirmed basic API endpoints continue to work

## Files Changed

- `docker-compose.dev.yml` - Updated backend command to use `run.py`
- `tests/test_websocket_config.py` - Added WebSocket configuration tests
- `tests/test_websocket_eventlet_fix.py` - Added eventlet-specific validation tests

## Production Impact

No changes needed for production environments - both `docker-compose.yml` and `docker-compose.prod.yml` already use the correct default command from the Dockerfile which runs `python run.py`.

## Testing the Fix

To verify the fix is working:

1. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up backend
   ```

2. Check logs for "Server initialized for eventlet" message

3. Test WebSocket connection (should no longer see eventlet errors)

The fix resolves the authentication black screen issue by ensuring WebSocket connections can be established properly after login.