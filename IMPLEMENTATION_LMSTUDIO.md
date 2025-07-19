# Implementation Guide: LM Studio Configuration Changes

## Overview
This guide provides step-by-step instructions for implementing the LM Studio configuration changes identified in the accidentally merged PR #141.

## Current State Analysis

### Files with localhost:1234 references that need updating:
1. `config/config.py` (line 48)
2. `app/__init__.py` (multiple references)
3. `app/api/llm_providers.py`
4. `.env.example` (line 26)
5. Test files in `tests/` directory

## Implementation Steps

### Step 1: Update Main Configuration (config/config.py)

**Current:**
```python
LMSTUDIO_API_BASE = os.environ.get("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
```

**Required Change:**
```python
LMSTUDIO_API_BASE = os.environ.get("LMSTUDIO_API_BASE", "http://192.168.1.98:1234/v1")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "lmstudio")
```

### Step 2: Update Environment Example (.env.example)

**Current:**
```bash
# LMStudio Configuration (when LLM_PROVIDER=lmstudio)
# LMSTUDIO_API_BASE=http://localhost:1234/v1  # Optional, defaults to localhost:1234
```

**Required Change:**
```bash
# LMStudio Configuration (when LLM_PROVIDER=lmstudio)
# LMSTUDIO_API_BASE=http://192.168.1.98:1234/v1  # Optional, defaults to 192.168.1.98:1234
```

**Also update the default provider:**
```bash
# Choose 'openai' or 'lmstudio'
LLM_PROVIDER=lmstudio
```

### Step 3: Update Application Factory (app/__init__.py)

Search for hardcoded localhost:1234 references and update them to use the configuration.

### Step 4: Update API Providers (app/api/llm_providers.py)

Ensure all LM Studio references use the configuration rather than hardcoded localhost.

### Step 5: Update Test Files

Update all test files that have hardcoded localhost:1234 references to use the new default or a test-specific configuration.

## Testing Checklist

- [ ] Verify LM Studio connection works with new IP address
- [ ] Test fallback behavior when LM Studio is not available
- [ ] Ensure OpenAI still works when explicitly configured
- [ ] Run all existing tests to ensure no regression
- [ ] Test Docker environment compatibility

## Validation Steps

1. **Environment Variable Test:**
   ```bash
   # Should show lmstudio as default
   python -c "from config.config import Config; print(Config.LLM_PROVIDER)"
   
   # Should show new IP address
   python -c "from config.config import Config; print(Config.LMSTUDIO_API_BASE)"
   ```

2. **Application Startup Test:**
   ```bash
   python run.py
   # Check logs for LM Studio initialization with new address
   ```

3. **API Test:**
   ```bash
   curl -X GET http://localhost:5000/api/llm-providers/status
   # Should show LM Studio as active provider
   ```

## Rollback Plan

If issues occur, revert these changes:
1. Change `LLM_PROVIDER` default back to "openai"
2. Change `LMSTUDIO_API_BASE` default back to "http://localhost:1234/v1"
3. Update `.env.example` documentation accordingly

## Related Files for Review

- `docs/llm/lmstudio_integration.md` - May need documentation updates
- Docker compose files - Ensure network configuration supports new IP
- Any deployment scripts that reference LM Studio configuration

## Security Considerations

- Ensure the new IP address (192.168.1.98) is accessible from the Docker environment
- Verify firewall settings allow communication on port 1234
- Consider if this IP should be configurable via environment variable for different deployments