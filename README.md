# Etsy Keyword Analyzer

A microservices-based application for analyzing Etsy keywords and market trends.

## Project Structure

```
etsy-keyword-analyzer/
├── src/
│   ├── api/           # FastAPI backend service
│   ├── workers/       # Background workers
│   │   ├── scraper/   # Etsy data scraping worker
│   │   └── email/     # Email notification worker
│   └── common/        # Shared utilities and configurations
├── client/           # React frontend application
└── tests/            # Test suites
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Redis
- RabbitMQ

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/etsy-keyword-analyzer.git
cd etsy-keyword-analyzer
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
docker compose up -d
```

## Development

### Backend (API)
```bash
cd src/api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
flask run
```

### Frontend (Client)
```bash
cd client
npm install
npm run dev
```

### Workers
```bash
cd src/workers/scraper
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python worker.py
```

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/api/
pytest tests/workers/
```

## License

MIT 