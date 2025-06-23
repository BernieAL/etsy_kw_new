# Etsy Keyword Monitoring Tool

A comprehensive monitoring system for Etsy listings that tracks changes in listing counts, seller prices, inventory, and descriptions.

## Environment Setup

Before running the application, you need to configure environment variables:

### 1. Create Environment File
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your configuration
nano .env
```

### 2. Required Environment Variables

#### For Local Development:
```bash
# Database Configuration
DATABASE_PATH=etsy_monitor.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring Configuration
DEFAULT_SCHEDULE_INTERVAL=3600
DEFAULT_NOTIFICATION_THRESHOLD=5
```

#### For Production Deployment:
```bash
# Server Configuration
VPS_IP=YOUR_VPS_IP_HERE
VPS_USER=root

# Database Configuration
DATABASE_PATH=/app/data/etsy_monitor.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Security Notes
- **Never commit `.env` files** to version control
- The `.gitignore` file already excludes `.env` files
- Database files (`*.db`) are also excluded from version control
- Update `env.example` when adding new environment variables

## Architecture Overview

The system consists of several key components:

### 1. **Etsy Scraper** (`etsy_scraper.py`)
- Scrapes Etsy search results for given keywords
- Extracts total listing count and individual listing details
- Uses Playwright with stealth measures to avoid detection
- Returns structured data including listing IDs, titles, prices, shops, and URLs

### 2. **Monitoring System** (`monitoring_system.py`)
- SQLite database for storing monitoring rules and historical data
- Tracks changes between scraping sessions
- Generates notifications for detected changes
- Supports multiple monitoring types:
  - **Listing count changes** (with configurable thresholds)
  - **Seller-specific monitoring** (price changes, new inventory, description changes)
  - **Multi-user support** with email-based filtering

### 3. **Monitoring Runner** (`monitor_runner.py`)
- Executes monitoring cycles for all active rules
- Integrates scraper with monitoring system
- Command-line interface for testing and management

### 4. **REST API** (`api/monitoring_api.py`)
- FastAPI-based REST API for managing monitoring rules
- CRUD operations for monitoring rules
- Endpoint to trigger monitoring cycles
- Notification retrieval

## Features

### Monitoring Capabilities

1. **Listing Count Monitoring**
   - Track total number of results for a keyword
   - Get notified when count increases/decreases by threshold amount
   - Example: "Notify me when 'pearl necklace' listings change by 10+ items"

2. **Seller-Specific Monitoring**
   - Monitor specific sellers for changes
   - Track price changes: "Seller A changed price from $50 to $45"
   - Track new inventory: "Seller B added new listing for 'pearl necklace'"
   - Track description changes: "Seller C updated listing title"

3. **Flexible Configuration**
   - Multiple monitoring rules per user
   - Configurable notification thresholds
   - Enable/disable specific monitoring types
   - Email-based user management

## Quick Start

### 1. Start the Container
```bash
# Start the persistent container
docker compose up -d backend
```

### 2. Create a Monitoring Rule
```bash
# Create an example monitoring rule
./run_monitoring.sh create-example
```

### 3. Run Monitoring Cycle
```bash
# Run monitoring for all active rules
./run_monitoring.sh run
```

### 4. Check Notifications
```bash
# View pending notifications
./run_monitoring.sh notifications
```

### 5. List All Rules
```bash
# View all monitoring rules
./run_monitoring.sh list-rules
```

## API Usage

### Start API Server
```bash
./run_api.sh
```

### API Endpoints

#### Create Monitoring Rule
```bash
curl -X POST "http://localhost:8000/monitoring-rules" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "pearl necklace",
    "user_email": "user@example.com",
    "monitor_listing_count": true,
    "monitor_sellers": ["PearlCraft", "OceanGems"],
    "monitor_price_changes": true,
    "monitor_inventory_changes": true,
    "notification_threshold": 5
  }'
```

#### List Monitoring Rules
```bash
curl "http://localhost:8000/monitoring-rules"
```

#### Run Monitoring Cycle
```bash
curl -X POST "http://localhost:8000/monitoring/run"
```

#### Get Notifications
```bash
curl "http://localhost:8000/notifications"
```

## Example Use Cases

### 1. **Competitive Intelligence**
- Monitor competitors' pricing for specific products
- Track when competitors add new inventory
- Get alerts for significant market changes

### 2. **Market Research**
- Track overall market size for product categories
- Monitor seasonal trends in listing counts
- Identify emerging product categories

### 3. **Price Optimization**
- Monitor price changes across similar products
- Track competitor pricing strategies
- Optimize pricing based on market movements

### 4. **Inventory Management**
- Monitor when specific sellers restock
- Track availability of rare or limited items
- Get alerts for new product releases

## Database Schema

### Monitoring Rules Table
- `id`: Unique rule identifier
- `keyword`: Search term to monitor
- `user_email`: User who owns the rule
- `monitor_listing_count`: Whether to monitor total results
- `monitor_sellers`: JSON array of seller names to monitor
- `monitor_price_changes`: Whether to track price changes
- `monitor_inventory_changes`: Whether to track new inventory
- `monitor_description_changes`: Whether to track listing changes
- `notification_threshold`: Minimum change threshold for notifications
- `created_at`: Rule creation timestamp
- `last_checked`: Last monitoring execution time
- `is_active`: Whether rule is active

### Historical Data Table
- Stores scraped data for each monitoring execution
- Enables change detection between runs
- Maintains audit trail of all monitoring activity

### Notifications Table
- Stores generated notifications
- Tracks notification status (sent/pending)
- Links notifications to specific rules

## Development Workflow

### 1. **Testing Scraper**
```bash
# Test scraper directly
./run_scraper.sh
```

### 2. **Testing Monitoring**
```bash
# Create test rule and run monitoring
./run_monitoring.sh create-example
./run_monitoring.sh run
```

### 3. **API Development**
```bash
# Start API server
./run_api.sh
# Access API docs at http://localhost:8000/docs
```

## Future Enhancements

1. **Email Notifications**
   - Integrate with email service (SendGrid, AWS SES)
   - Scheduled notification delivery
   - Customizable notification formats

2. **Web Dashboard**
   - React/Vue frontend for rule management
   - Real-time monitoring dashboard
   - Historical data visualization

3. **Advanced Monitoring**
   - Image change detection
   - Review/rating monitoring
   - Shipping cost tracking

4. **Scheduling**
   - Cron-based automatic monitoring
   - Configurable monitoring frequencies
   - Time-based monitoring rules

5. **Analytics**
   - Trend analysis and reporting
   - Price prediction models
   - Market opportunity identification

## Troubleshooting

### Common Issues

1. **Scraper Fails**
   - Check if Etsy is blocking requests
   - Verify Playwright browser setup
   - Check for HTML structure changes

2. **Database Issues**
   - Ensure SQLite database is writable
   - Check database file permissions
   - Verify table schema

3. **API Connection Issues**
   - Check if API server is running
   - Verify port 8000 is accessible
   - Check Docker container status

### Debug Commands
```bash
# Check container logs
docker compose logs backend

# Access container shell
docker compose exec backend bash

# Check database
docker compose exec backend sqlite3 etsy_monitor.db ".tables"
```

## License

This project is for educational and research purposes. Please respect Etsy's terms of service and rate limiting policies.