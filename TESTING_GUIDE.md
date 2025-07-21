# Manual Testing Guide for LMStudio Chat Integration Fixes

This guide helps you verify that the WebSocket connection and chat message processing issues have been resolved.

## Prerequisites

1. Have BigShot running (backend + frontend)
2. Have LMStudio installed and running locally
3. Browser developer tools open to monitor console and network activity

## Test 1: WebSocket Connection After Login

**Expected Behavior**: WebSocket should connect successfully after login, not before.

**Steps**:
1. Open BigShot in browser (clear localStorage if needed)
2. Open browser DevTools → Console tab
3. Navigate to login page
4. **Before login**: Should see message "WebSocket connection attempted without auth token. Will retry after login."
5. **Login with admin/password**
6. **After login**: Should see "Refreshing WebSocket connection with new auth token" and "WebSocket connected"
7. **Verify**: No "WebSocket connection failed" errors in console

## Test 2: Chat Message Error Handling

**Expected Behavior**: Instead of "NoneType object is not subscriptable" error, should get descriptive error messages.

**Steps**:
1. Ensure you're logged in
2. Go to Chat interface  
3. **If LMStudio is NOT running**: 
   - Send a chat message (e.g., "help")
   - Should get "LLM service is temporarily unavailable" error instead of 500 error
4. **If LMStudio is running but misconfigured**:
   - Send a chat message
   - Should get proper error message instead of "NoneType" error

## Test 3: LMStudio Provider Configuration

**Expected Behavior**: Provider configuration and testing should work reliably.

**Steps**:
1. Go to Settings → LLM Providers
2. Look for "LMStudio Local" provider
3. Click "Test Connection"
4. **If LMStudio running**: Should get successful test result with response time
5. **If LMStudio not running**: Should get clear connection error, not crash

## Test 4: Chat with Working LMStudio

**Expected Behavior**: Chat should work normally when LMStudio is properly configured.

**Steps**:
1. Ensure LMStudio is running with a model loaded
2. Go to Settings → LLM Providers  
3. Configure LMStudio provider with correct URL (e.g., http://localhost:1234/v1)
4. Test and activate the provider
5. Go to Chat interface
6. Send message: "Hello, can you help me?"
7. Should receive proper response from LMStudio

## Test 5: WebSocket Reconnection

**Expected Behavior**: WebSocket should reconnect properly when authentication changes.

**Steps**:
1. Log in and verify WebSocket is connected
2. Log out
3. **Verify**: WebSocket disconnects (check DevTools console)
4. Log in again  
5. **Verify**: WebSocket reconnects automatically

## Expected Console Messages

**Good WebSocket Flow**:
```
WebSocket connection attempted without auth token. Will retry after login.
Refreshing WebSocket connection with new auth token  
WebSocket connected
```

**Good Chat Error (LLM unavailable)**:
```
HTTP 503: LLM service is temporarily unavailable. Please try again later.
```

**Bad Patterns (should NOT see these)**:
```
WebSocket connection to 'ws://localhost:3000/?token=...' failed
NoneType object is not subscriptable
Failed to process message: 'NoneType' object is not subscriptable
```

## Troubleshooting

**If WebSocket still fails**:
- Check browser DevTools → Network tab for WebSocket connection attempts
- Verify auth token is stored in localStorage after login
- Check browser console for authentication errors

**If chat still gives NoneType errors**:
- This indicates the fix wasn't applied correctly
- Check that the backend was restarted after the code changes
- Verify the latest version of the code is running

**If LMStudio connection fails**:
- Verify LMStudio is running on the correct port (usually 1234)
- Check LMStudio server logs for connection attempts
- Ensure the base URL in provider config matches LMStudio's address

## Success Criteria

✅ **WebSocket connects after login, not before**  
✅ **No "NoneType object is not subscriptable" errors**  
✅ **Descriptive error messages for LLM failures**  
✅ **WebSocket disconnects on logout and reconnects on login**  
✅ **Chat works properly when LMStudio is configured correctly**  

If all criteria pass, the issues have been successfully resolved!