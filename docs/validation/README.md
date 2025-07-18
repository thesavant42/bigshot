# Docker Configuration Validation

This directory contains scripts and documentation for validating the BigShot Docker configuration.

## Files

- `docker-networking.md` - Comprehensive documentation for Docker networking setup
- `validate_docker_config.sh` - Validation script to test Docker configuration

## Validation Script

The validation script (`/tmp/validate_docker_config.sh`) performs the following checks:

1. **Docker Compose Configuration Validation**
   - Syntax validation for all compose files
   - Service definition verification

2. **Frontend Configuration Testing**
   - Vite proxy configuration
   - Nginx proxy configuration
   - External connection support

3. **Build Process Verification**
   - NPM dependency installation
   - Frontend build process
   - Docker image creation

4. **Environment Detection Testing**
   - Smart URL detection logic
   - Development vs production scenarios

5. **Configuration Consistency**
   - Service naming consistency
   - Port mapping verification

6. **Documentation Coverage**
   - Presence of required documentation
   - Content validation

## Usage

```bash
# Run validation from project root
cd /home/runner/work/bigshot/bigshot
/tmp/validate_docker_config.sh
```

## Expected Output

When all tests pass, you should see:
```
=== Validation Summary ===
All critical tests passed! ✓

The frontend-backend communication should work correctly in Docker deployments.
```

## Common Issues Resolved

1. **Vite Proxy Port Mismatch**: Fixed target from `localhost:5001` to `localhost:5000`
2. **External Connection Support**: Added `host: '0.0.0.0'` to Vite configuration
3. **Environment Detection**: Validated smart URL detection for all deployment scenarios
4. **Docker Networking**: Confirmed proper service-to-service communication setup