# Factur-X Express - Entry Points and Startup Commands

## Application Entry Points

### Backend (FastAPI)

#### Main Entry Point
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import invoices, auth, health
from src.core.config import settings
from src.core.database import engine
from src.models import Base

app = FastAPI(
    title="Factur-X Express API",
    description="API for generating and managing Factur-X invoices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"])

# Create database tables
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

#### Development Startup
```bash
# Method 1: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using FastAPI CLI
fastapi dev src/main.py

# Method 3: Using Python module
python -m src.main

# Method 4: With environment file
uvicorn src.main:app --reload --env-file .env.development
```

#### Production Startup
```bash
# Using Gunicorn with Uvicorn workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Uvicorn with production settings
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Docker
docker run -p 8000:8000 facturx-backend
```

### Frontend (Next.js)

#### Main Entry Point
```typescript
// pages/_app.tsx
import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../src/contexts/AuthContext';
import { ToastProvider } from '../src/contexts/ToastContext';
import '../src/styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <Component {...pageProps} />
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
```

```typescript
// pages/index.tsx
import { NextPage } from 'next';
import { DashboardLayout } from '../src/components/layouts/DashboardLayout';
import { InvoiceList } from '../src/components/invoices/InvoiceList';

const HomePage: NextPage = () => {
  return (
    <DashboardLayout>
      <h1>Factur-X Express Dashboard</h1>
      <InvoiceList />
    </DashboardLayout>
  );
};

export default HomePage;
```

#### Development Startup
```bash
# Method 1: Using npm
npm run dev

# Method 2: Using yarn
yarn dev

# Method 3: Using pnpm
pnpm dev

# Method 4: With custom port
npm run dev -- --port 3001

# Method 5: With turbo (if using)
npm run dev --turbo
```

#### Production Startup
```bash
# Build and start
npm run build
npm start

# Using PM2
pm2 start npm --name "facturx-frontend" -- start

# Using Docker
docker run -p 3000:3000 facturx-frontend
```

### Worker Service (Optional)

#### Main Entry Point
```python
# worker/src/main.py
import asyncio
from celery import Celery
from src.core.config import settings
from src.tasks.invoice_processing import process_invoice_task
from src.tasks.email_notifications import send_email_task

# Celery configuration
celery_app = Celery(
    "facturx_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.tasks.invoice_processing",
        "src.tasks.email_notifications",
        "src.tasks.pdf_generation"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "src.tasks.invoice_processing.*": {"queue": "invoice_processing"},
        "src.tasks.email_notifications.*": {"queue": "notifications"},
    }
)

if __name__ == "__main__":
    celery_app.start()
```

#### Worker Startup
```bash
# Start Celery worker
celery -A src.main worker --loglevel=info

# Start with specific queues
celery -A src.main worker --loglevel=info --queues=invoice_processing,notifications

# Start Celery beat (scheduler)
celery -A src.main beat --loglevel=info

# Start flower (monitoring)
celery -A src.main flower --port=5555

# Production with multiple workers
celery multi start worker1 worker2 -A src.main --loglevel=info
```

## Docker Entry Points

### Backend Dockerfile
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Entry point
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
# Dockerfile.frontend
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

# Entry point
CMD ["npm", "start"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/facturx
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev

  worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/facturx
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: celery -A src.main worker --loglevel=info

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=facturx
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Environment Configuration

### Backend Environment Variables
```bash
# .env.development
DATABASE_URL=postgresql://user:password@localhost:5432/facturx_dev
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000"]
DEBUG=true
LOG_LEVEL=debug

# Factur-X specific
FACTURX_TEMPLATE_PATH=/app/templates
PDF_GENERATION_TIMEOUT=30
MAX_FILE_SIZE=10485760  # 10MB
```

### Frontend Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Factur-X Express"
NEXT_PUBLIC_VERSION=1.0.0
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

## Health Check Endpoints

### Backend Health Check
```python
# src/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "facturx-backend"}

@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

### Frontend Health Check
```typescript
// pages/api/health.ts
import type { NextApiRequest, NextApiResponse } from 'next';

type HealthResponse = {
  status: string;
  service: string;
  timestamp: string;
};

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  res.status(200).json({
    status: 'healthy',
    service: 'facturx-frontend',
    timestamp: new Date().toISOString(),
  });
}
```

## Monitoring and Logging

### Application Startup Logs
```python
# Backend logging configuration
import logging
from src.core.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/application.log")
    ]
)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Factur-X Express Backend")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info("Application startup complete")
```

## Quick Start Commands

### Full Stack Development
```bash
# Terminal 1: Start database and Redis
docker-compose up db redis

# Terminal 2: Start backend
cd apps/backend
uvicorn src.main:app --reload

# Terminal 3: Start frontend
cd apps/frontend
npm run dev

# Terminal 4: Start worker (optional)
cd apps/worker
celery -A src.main worker --loglevel=info
```

### Using Docker Compose
```bash
# Start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```