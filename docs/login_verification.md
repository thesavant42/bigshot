# Login Verification Guide

This guide provides step-by-step instructions for verifying the login functionality and backend connectivity in BigShot.

## Test Credentials

For all test cases, use the following default credentials:
- **Username:** `admin`
- **Password:** `password`

> ⚠️ **IMPORTANT:** Change the default password immediately in production environments!

## Step-by-Step Login Verification

### 1. Navigate to Login Page
- Open your web browser
- Navigate to the BigShot application URL (typically `http://localhost` or your deployment URL)
- You should see the BigShot login screen with the application logo

### 2. Enter Credentials
- In the **Username** field, enter: `admin`
- In the **Password** field, enter: `password`
- Ensure both fields are filled correctly

### 3. Submit Login
- Click the **"Sign In"** button
- The login process should begin with a loading indicator

### 4. Post-Authentication Verification Page
After successful login, you should be automatically redirected to a **Post-Authentication Verification** page that displays:

#### Authentication Status Section
- ✅ **Status:** SUCCESS
- **User:** admin
- **Timestamp:** Current login time
- **Message:** "Authentication successful - JWT token verified"

#### Backend Services Status Section
The page should show the status of all backend services:
- **Database:** ✅ HEALTHY - "Database connection successful"
- **Redis:** ✅ HEALTHY - "Redis connection successful"  
- **Celery:** ✅ HEALTHY or ⚠️ DEGRADED - Shows worker status

#### Environment Information Section
- **Service:** bigshot
- **Hostname:** Container or system hostname
- **Environment:** production/development
- **Container:** Container ID (if running in Docker)

#### Overall System Health Section
- **Status:** HEALTHY (if all services are working)
- **Services:** X/Y services healthy

#### Verification Instructions Section
The page includes a blue info box confirming:
- ✅ Login successful with credentials: admin/password
- ✅ JWT token verified and backend connectivity confirmed
- ✅ All required services are accessible and responding

### 5. Proof Documentation
This post-authentication page serves as **proof of connectivity**. You should:
- **Take a screenshot** of the entire verification page
- **Print the page** using the "🖨️ Print Proof" button (optional)
- **Note the timestamp** and overall health status

### 6. Continue to Application
- The page will automatically advance to the main application in 10 seconds
- You can manually continue by clicking **"Continue to Application →"**
- You can pause auto-advance using the **"⏸️ Pause Auto-Advance"** button

### 7. Main Application Access
After continuing, you should see:
- The main BigShot dashboard with domain reconnaissance tools
- Chat interface on the left panel
- Domain management on the right panel
- Navigation menu and user controls

## Troubleshooting Login Issues

### Login Failure Scenarios

#### Invalid Credentials
- **Error Message:** "Login failed. Please check your credentials."
- **Solution:** Verify username is `admin` and password is `password`
- **Check:** Ensure caps lock is off and no extra spaces

#### Backend Connectivity Issues
- **Symptoms:** Login succeeds but verification page shows service failures
- **Check:** Backend services status in the verification page
- **Common Issues:**
  - ❌ Database: Check PostgreSQL connection
  - ❌ Redis: Check Redis server status
  - ❌ Celery: Check worker processes

#### Complete Login Failure
- **Symptoms:** Cannot reach login page or server errors
- **Check:** 
  - Backend server is running (port 5000)
  - Frontend server is running (port 80)
  - Network connectivity
  - Docker containers are healthy

### Debug Information

When reporting issues, include:
1. **Screenshot** of the error or verification page
2. **Browser console errors** (F12 → Console tab)
3. **Network requests** (F12 → Network tab)
4. **Backend logs** from the application logs
5. **Environment details** (Docker, local development, etc.)

### Container Diagnostics

For Docker deployments, run diagnostic scripts:

```bash
# Run diagnostics on all containers
./scripts/run_diagnostics_all.sh

# Run diagnostics on specific container
docker exec <container_name> /usr/local/bin/container_diagnostics.sh
```

### Log Analysis

Check application logs for detailed debugging:
```bash
# View recent logs
tail -f logs/app.log

# Search for authentication events
grep "AUTH" logs/app.log

# Search for connectivity issues
grep "connectivity" logs/app.log
```

## Expected Verification Results

### Successful Login Verification
- ✅ Authentication status shows SUCCESS
- ✅ All backend services show HEALTHY status
- ✅ Environment information is populated
- ✅ Overall status shows HEALTHY
- ✅ Auto-advance to main application works

### Partial Success (Degraded Mode)
- ✅ Authentication successful
- ⚠️ Some services show DEGRADED status
- ✅ Core functionality available
- **Action:** Investigate degraded services

### Complete Failure
- ❌ Login fails at credential verification
- ❌ Cannot reach verification page
- ❌ Multiple services show FAILED status
- **Action:** Check infrastructure and logs

## Security Notes

1. **Default Credentials:** The admin/password combination is for initial setup only
2. **Production Security:** Change default password immediately in production
3. **Token Security:** JWT tokens are used for session management
4. **Connection Security:** All backend connections are verified before allowing access

## Additional Verification Steps

### Manual Backend Verification
You can manually verify backend connectivity:

1. **Health Check Endpoint:** Visit `/api/v1/health`
2. **Detailed Health:** Visit `/api/v1/health/detailed` (requires login)
3. **Metrics:** Visit `/api/v1/metrics` for system metrics

### API Testing
Test the authentication API directly:
```bash
# Login and get token
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Test connectivity proof
curl -X GET http://localhost:5000/api/v1/auth/connectivity-proof \
  -H "Authorization: Bearer <your-jwt-token>"
```

This verification process ensures that:
- Authentication system is working correctly
- All backend services are properly connected
- The application is ready for normal operation
- Any configuration issues are identified early

Keep this verification page screenshot as proof of successful deployment and connectivity verification.