# API Documentation

## Overview

The BigShot API provides RESTful endpoints for managing domains, enumeration jobs, configuration, and authentication. The API follows REST conventions and returns JSON responses.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All API endpoints (except health check) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

### Getting a Token

**POST** `/auth/login`

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "username": "admin"
    }
  }
}
```

## Response Format

All responses follow this format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 50,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

## Endpoints

### Authentication

#### Login
**POST** `/auth/login`

Authenticate and get access token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "user": {
      "username": "admin"
    }
  }
}
```

#### Get Profile
**GET** `/auth/profile`

Get current user profile.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "username": "admin",
    "active": true
  }
}
```

#### Verify Token
**POST** `/auth/verify`

Verify if the current token is valid.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": "admin"
  }
}
```

### Domains

#### List Domains
**GET** `/domains`

Get all domains with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50)
- `root_domain` (string): Filter by root domain
- `source` (string): Filter by enumeration source
- `search` (string): Search in domain names and tags

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "root_domain": "example.com",
      "subdomain": "www.example.com",
      "source": "crt.sh",
      "tags": ["production", "verified"],
      "cdx_indexed": false,
      "fetched_at": "2024-01-15T12:00:00Z",
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### Get Domain
**GET** `/domains/{id}`

Get a specific domain by ID.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "root_domain": "example.com",
    "subdomain": "www.example.com",
    "source": "crt.sh",
    "tags": ["production"],
    "cdx_indexed": false,
    "fetched_at": "2024-01-15T12:00:00Z",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

#### Create Domain
**POST** `/domains`

Create a new domain.

**Request:**
```json
{
  "root_domain": "example.com",
  "subdomain": "api.example.com",
  "source": "crt.sh",
  "tags": ["api", "production"],
  "cdx_indexed": false
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "root_domain": "example.com",
    "subdomain": "api.example.com",
    "source": "crt.sh",
    "tags": ["api", "production"],
    "cdx_indexed": false,
    "fetched_at": "2024-01-15T12:00:00Z",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

#### Update Domain
**PUT** `/domains/{id}`

Update an existing domain.

**Request:**
```json
{
  "tags": ["updated", "production"],
  "cdx_indexed": true
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "root_domain": "example.com",
    "subdomain": "www.example.com",
    "source": "crt.sh",
    "tags": ["updated", "production"],
    "cdx_indexed": true,
    "fetched_at": "2024-01-15T12:00:00Z",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:30:00Z"
  }
}
```

#### Delete Domain
**DELETE** `/domains/{id}`

Delete a domain.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Domain deleted successfully"
  }
}
```

#### Start Domain Enumeration
**POST** `/domains/enumerate`

Start a new domain enumeration job.

**Request:**
```json
{
  "domains": ["example.com", "test.com"],
  "sources": ["crt.sh", "virustotal", "shodan"],
  "options": {
    "include_wildcards": true,
    "max_depth": 3,
    "timeout": 300
  }
}
```

**Response:** `202 Accepted`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "type": "domain_enumeration",
    "domain": "example.com,test.com",
    "status": "pending",
    "progress": 0,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

#### Get Domain Hierarchy
**GET** `/domains/hierarchy/{root_domain}`

Get hierarchical domain structure for a root domain.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "com": {
      "domains": [],
      "children": {
        "example": {
          "domains": [
            {
              "id": 1,
              "root_domain": "example.com",
              "subdomain": "example.com",
              "source": "crt.sh",
              "tags": []
            }
          ],
          "children": {
            "www": {
              "domains": [
                {
                  "id": 2,
                  "root_domain": "example.com",
                  "subdomain": "www.example.com",
                  "source": "crt.sh",
                  "tags": []
                }
              ],
              "children": {}
            }
          }
        }
      }
    }
  }
}
```

#### Bulk Operations
**POST** `/domains/bulk`

Perform bulk operations on multiple domains.

**Request:**
```json
{
  "operation": "update_tags",
  "domain_ids": [1, 2, 3],
  "tags": ["bulk_updated", "production"]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Bulk update_tags completed successfully"
  }
}
```

### Jobs

#### List Jobs
**GET** `/jobs`

Get all jobs with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50)
- `status` (string): Filter by job status
- `type` (string): Filter by job type
- `domain` (string): Filter by domain

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "domain_enumeration",
      "domain": "example.com",
      "status": "completed",
      "progress": 100,
      "result": "{\"total_found\": 47, \"domains_found\": [...]}",
      "error_message": null,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:05:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### Get Job
**GET** `/jobs/{id}`

Get a specific job by ID.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "type": "domain_enumeration",
    "domain": "example.com",
    "status": "completed",
    "progress": 100,
    "result": "{\"total_found\": 47}",
    "error_message": null,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:05:00Z"
  }
}
```

#### Cancel Job
**POST** `/jobs/{id}/cancel`

Cancel a running job.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Job cancelled successfully"
  }
}
```

#### Get Job Logs
**GET** `/jobs/{id}/logs`

Get logs for a specific job.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "job_id": 1,
    "logs": [
      {
        "timestamp": "2024-01-15T12:00:00Z",
        "level": "INFO",
        "message": "Job 1 created for domain(s): example.com"
      },
      {
        "timestamp": "2024-01-15T12:01:00Z",
        "level": "INFO",
        "message": "Job 1 started enumeration"
      }
    ]
  }
}
```

#### Get Job Status
**GET** `/jobs/{id}/status`

Get detailed status for a specific job.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "job": {
      "id": 1,
      "type": "domain_enumeration",
      "status": "running",
      "progress": 65
    },
    "detailed_status": {
      "id": 1,
      "type": "domain_enumeration",
      "domain": "example.com",
      "status": "running",
      "progress": 65,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:03:00Z",
      "estimated_completion": "2024-01-15T12:05:00Z"
    }
  }
}
```

#### Get Job Results
**GET** `/jobs/{id}/results`

Get results for a completed job.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "job_id": 1,
    "results": {
      "total_found": 47,
      "domains_found": [
        "www.example.com",
        "api.example.com",
        "mail.example.com"
      ]
    }
  }
}
```

#### Get Job Statistics
**GET** `/jobs/stats`

Get job statistics.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "status_counts": {
      "completed": 25,
      "pending": 2,
      "running": 1,
      "failed": 3
    },
    "type_counts": {
      "domain_enumeration": 31
    },
    "recent_jobs": [
      {
        "id": 31,
        "type": "domain_enumeration",
        "status": "completed",
        "created_at": "2024-01-15T12:00:00Z"
      }
    ]
  }
}
```

### Configuration

#### Get API Keys
**GET** `/config/api-keys`

Get all configured API keys (values are masked for security).

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "service": "virustotal",
      "key_masked": "12345678...",
      "is_active": true,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

#### Get API Key
**GET** `/config/api-keys/{service}`

Get a specific API key by service name.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "service": "virustotal",
    "key_masked": "12345678...",
    "is_active": true,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

#### Update API Key
**PUT** `/config/api-keys/{service}`

Create or update an API key.

**Request:**
```json
{
  "key_value": "your_api_key_here"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "service": "virustotal",
    "key_masked": "your_api_...",
    "is_active": true,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:30:00Z"
  }
}
```

#### Delete API Key
**DELETE** `/config/api-keys/{service}`

Delete an API key.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "API key deleted successfully"
  }
}
```

#### Test API Key
**POST** `/config/api-keys/{service}/test`

Test an API key.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "service": "virustotal",
    "test_result": {
      "valid": true,
      "domains_found": 23
    }
  }
}
```

#### Get Settings
**GET** `/config/settings`

Get application settings.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "rate_limit_enabled": true,
    "jwt_expires": 3600,
    "supported_sources": ["crt.sh", "virustotal", "shodan"]
  }
}
```

#### Update Settings
**PUT** `/config/settings`

Update application settings.

**Request:**
```json
{
  "rate_limit_enabled": false,
  "jwt_expires": 7200
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Settings updated successfully"
  }
}
```

#### Health Check
**GET** `/config/health`

Check application health status.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `HTTP_400` | Bad Request - Invalid input |
| `HTTP_401` | Unauthorized - Invalid credentials |
| `HTTP_403` | Forbidden - Access denied |
| `HTTP_404` | Not Found - Resource not found |
| `HTTP_409` | Conflict - Resource already exists |
| `HTTP_422` | Unprocessable Entity - Validation error |
| `HTTP_500` | Internal Server Error |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **Enumeration**: 10 concurrent jobs per user

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## External Service Integration

### Supported Sources

1. **crt.sh** - Certificate Transparency logs (no API key required)
2. **VirusTotal** - Requires API key
3. **Shodan** - Requires API key

### API Key Configuration

Configure external service API keys through the `/config/api-keys` endpoints. Keys are encrypted at rest and validated before use.

## WebSocket Support

Real-time updates for job progress are available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:5000/api/v1/ws/jobs/{job_id}');
ws.onmessage = function(event) {
  const update = JSON.parse(event.data);
  console.log('Job progress:', update.progress);
};
```

## Examples

### Complete Domain Enumeration Workflow

```bash
# 1. Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Start enumeration
curl -X POST http://localhost:5000/api/v1/domains/enumerate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"domains": ["example.com"], "sources": ["crt.sh"]}'

# 3. Check job status
curl -X GET http://localhost:5000/api/v1/jobs/1/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Get results
curl -X GET http://localhost:5000/api/v1/jobs/1/results \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. List discovered domains
curl -X GET http://localhost:5000/api/v1/domains?root_domain=example.com \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bulk Domain Operations

```bash
# Get domain IDs
curl -X GET http://localhost:5000/api/v1/domains \
  -H "Authorization: Bearer YOUR_TOKEN"

# Bulk update tags
curl -X POST http://localhost:5000/api/v1/domains/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"operation": "update_tags", "domain_ids": [1,2,3], "tags": ["production"]}'
```

### API Key Management

```bash
# Set VirusTotal API key
curl -X PUT http://localhost:5000/api/v1/config/api-keys/virustotal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key_value": "your_virustotal_api_key"}'

# Test API key
curl -X POST http://localhost:5000/api/v1/config/api-keys/virustotal/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```