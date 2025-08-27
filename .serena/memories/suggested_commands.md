# Factur-X Express - Suggested Development Commands

## Project Setup
```bash
# Clone and setup project
git clone <repository-url>
cd facturx-express

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
# OR if using Poetry
poetry install

# Setup Node.js dependencies
npm install
# OR
yarn install
```

## Development Commands

### Python/FastAPI Backend
```bash
# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with specific environment
uvicorn main:app --reload --env-file .env.development

# Alternative with FastAPI CLI
fastapi dev main.py
```

### Next.js Frontend
```bash
# Start development server
npm run dev
# OR
yarn dev

# Build for production
npm run build
yarn build

# Start production server
npm start
yarn start
```

## Code Quality & Linting

### Python
```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint src/

# Type checking
mypy src/

# All quality checks
black . && isort . && flake8 . && mypy src/
```

### JavaScript/TypeScript
```bash
# Lint code
npm run lint
yarn lint

# Format code
npm run format
yarn format

# Type checking
npm run type-check
yarn type-check

# Fix linting issues
npm run lint:fix
yarn lint:fix
```

## Testing

### Python Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_invoices.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### JavaScript/TypeScript Tests
```bash
# Run all tests
npm test
yarn test

# Run tests in watch mode
npm run test:watch
yarn test:watch

# Run tests with coverage
npm run test:coverage
yarn test:coverage

# Run E2E tests
npm run test:e2e
yarn test:e2e
```

## Docker Commands

### Development
```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

### Production
```bash
# Build production images
docker build -t facturx-backend -f Dockerfile.backend .
docker build -t facturx-frontend -f Dockerfile.frontend .

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

## Database Commands

### PostgreSQL
```bash
# Start PostgreSQL with Docker
docker run --name facturx-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Connect to database
psql -h localhost -U postgres -d facturx

# Run migrations (if using Alembic)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add invoice table"
```

## Factur-X Specific Commands

### Python factur-x Library
```bash
# Install factur-x library
pip install factur-x

# Generate Factur-X invoice (example)
python -c "from facturx import generate_facturx_from_file; generate_facturx_from_file('invoice.pdf', 'metadata.xml')"
```

### Java Mustangproject
```bash
# Compile Java components
mvn compile
# OR
gradle build

# Run Mustangproject validation
java -jar mustangproject.jar --validate invoice.pdf
```

## Utility Commands

### Project Management
```bash
# Check project structure
tree -I 'node_modules|__pycache__|.git'

# Check disk usage
du -sh .

# Clean build artifacts
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf node_modules/.cache
```

### Performance & Monitoring
```bash
# Monitor system resources
top
htop

# Check port usage
lsof -i :8000
lsof -i :3000

# Monitor logs
tail -f logs/application.log
```

## CI/CD Commands

### GitHub Actions (Local Testing)
```bash
# Install act for local GitHub Actions testing
brew install act

# Run GitHub Actions locally
act

# Run specific workflow
act -W .github/workflows/ci.yml
```

### Deployment
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Health check
curl -f http://localhost:8000/health
```