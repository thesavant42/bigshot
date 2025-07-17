# User Guide

This guide provides step-by-step instructions for using the BigShot application.

## Getting Started

### First Time Setup

1. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:3000` (development) or your deployed URL
   - You should see the login screen

2. **Login**
   - Enter your username and password
   - Click "Login" to access the dashboard
   - Default credentials (development): `admin` / `password`

3. **Dashboard Overview**
   - The main dashboard shows your domain enumeration projects
   - Navigation menu provides access to different features
   - Real-time status updates appear in the top bar

## Domain Enumeration

### Adding a New Domain

1. **Navigate to Domains**
   - Click "Domains" in the navigation menu
   - Click "Add Domain" button

2. **Enter Domain Information**
   - **Root Domain**: Enter the primary domain (e.g., `example.com`)
   - **Source**: Select enumeration source (e.g., `crt.sh`, `subfinder`)
   - **Tags**: Add optional tags for organization
   - Click "Add Domain" to start enumeration

3. **Monitor Progress**
   - Domain enumeration runs in the background
   - Progress is shown in real-time
   - Results appear as subdomains are discovered

### Managing Domains

#### Viewing Domain Details
1. Click on any domain in the domains list
2. View detailed information:
   - Subdomain list
   - Discovery source
   - Timestamps
   - Status information

#### Filtering and Search
- Use the search bar to filter domains
- Filter by status (active, inactive, processing)
- Sort by date, name, or source

#### Exporting Data
1. Select domains you want to export
2. Click "Export" button
3. Choose format (CSV, JSON, XML)
4. Download the file

## AI Chat Interface

### Starting a Conversation

1. **Access Chat**
   - Click "Chat" in the navigation menu
   - The chat interface opens with a text input

2. **Send Messages**
   - Type your question or command
   - Press Enter or click "Send"
   - AI responses appear in real-time

### Chat Commands

#### Domain Intelligence
```
Find subdomains for example.com
Show me domains containing "api"
List all active domains
```

#### Domain Analysis
```
Analyze security for example.com
Check SSL certificates for my domains
Find expired domains
```

#### Data Queries
```
Show domains added today
Export domains as CSV
Count subdomains by source
```

### Chat Features

#### Context Awareness
- Chat remembers previous conversations
- Reference previous queries in follow-up questions
- Maintains context across sessions

#### Real-time Updates
- Live updates as domains are discovered
- Notifications for completed tasks
- Status changes appear immediately

## Job Management

### Background Tasks

1. **View Active Jobs**
   - Navigate to "Jobs" section
   - See all running and completed tasks
   - Monitor progress and status

2. **Job Types**
   - **Domain Enumeration**: Subdomain discovery
   - **Data Processing**: Analysis and cleanup
   - **Export Tasks**: Data export operations
   - **Notifications**: Email and webhook alerts

### Managing Jobs

#### Starting Jobs
- Jobs start automatically when adding domains
- Manual job creation available via API
- Batch operations for multiple domains

#### Monitoring Progress
- Real-time progress bars
- Estimated completion time
- Current task status

#### Job History
- View completed jobs
- Access job logs and results
- Retry failed jobs

## Data Management

### Organization

#### Tags and Labels
- Add tags to domains for organization
- Filter and search by tags
- Bulk tag operations

#### Sources
- Track where domains were discovered
- Filter by enumeration source
- Compare source effectiveness

### Data Export

#### Export Options
1. **CSV Format**
   - Spreadsheet-compatible
   - Custom column selection
   - Filtering options

2. **JSON Format**
   - API-compatible format
   - Full data structure
   - Programmatic processing

3. **XML Format**
   - Structured data format
   - Custom schema support
   - Integration-friendly

#### Automated Exports
- Schedule regular exports
- Email delivery options
- Webhook notifications

## Settings and Configuration

### User Preferences

1. **Access Settings**
   - Click user menu (top right)
   - Select "Settings"

2. **General Settings**
   - Theme selection (light/dark)
   - Notification preferences
   - Default view options

3. **API Configuration**
   - API key management
   - Rate limiting settings
   - Integration options

### Security Settings

#### Authentication
- Change password
- Two-factor authentication
- Session management

#### API Security
- Generate API keys
- Set access permissions
- Monitor API usage

## Advanced Features

### API Integration

#### Authentication
```bash
# Get access token
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

#### Domain Operations
```bash
# List domains
curl -X GET http://localhost:5000/api/v1/domains \
  -H "Authorization: Bearer YOUR_TOKEN"

# Add domain
curl -X POST http://localhost:5000/api/v1/domains \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"root_domain": "example.com", "source": "manual"}'
```

### Automation

#### Webhooks
- Configure webhook URLs
- Receive notifications on events
- Custom payload formatting

#### Scheduled Tasks
- Set up recurring enumerations
- Automated data cleanup
- Regular export schedules

## Troubleshooting

### Common Issues

#### Login Problems
- **Issue**: Cannot login with credentials
- **Solution**: Check username/password, verify account is active
- **Contact**: Check with administrator

#### Slow Performance
- **Issue**: Application is slow to respond
- **Solution**: Check server resources, refresh browser
- **Contact**: Report performance issues

#### Missing Data
- **Issue**: Domains or data not appearing
- **Solution**: Refresh page, check job status
- **Contact**: Check job logs for errors

### Getting Help

#### Support Channels
- **Documentation**: Check this guide and API docs
- **Issues**: Submit GitHub issues for bugs
- **Community**: Join discussions for questions

#### Logging
- Application logs available in admin panel
- Export logs for troubleshooting
- Error tracking and monitoring

## Best Practices

### Domain Management
- Use descriptive tags for organization
- Regular cleanup of old domains
- Monitor enumeration sources

### Security
- Change default passwords
- Regular security updates
- Monitor API usage

### Performance
- Limit concurrent enumerations
- Regular database maintenance
- Monitor resource usage

## Updates and Maintenance

### Staying Updated
- Check release notes regularly
- Subscribe to update notifications
- Test in development first

### Backup
- Regular data backups
- Export important data
- Test restore procedures

### Monitoring
- Set up health checks
- Monitor performance metrics
- Configure alerts