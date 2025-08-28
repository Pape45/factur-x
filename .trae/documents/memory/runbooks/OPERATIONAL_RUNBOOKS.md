# Operational Runbooks

## Overview
This document contains step-by-step operational procedures for deploying, monitoring, and maintaining the Factur-X Express system.

---

## Table of Contents
1. [Deployment Procedures](#deployment-procedures)
2. [Monitoring & Alerting](#monitoring--alerting)
3. [Incident Response](#incident-response)
4. [Backup & Recovery](#backup--recovery)
5. [Security Operations](#security-operations)
6. [Performance Tuning](#performance-tuning)
7. [Compliance Operations](#compliance-operations)

---

## Deployment Procedures

### 1.1 Development Environment Setup

**Prerequisites:**
- Docker Desktop installed
- Python 3.11+ with uv package manager
- Node.js 18+ with npm/yarn
- AWS CLI configured
- Git access to repository

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/company/facturx-express.git
cd facturx-express

# 2. Setup Python environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements-dev.txt

# 3. Setup environment variables
cp .env.example .env.local
# Edit .env.local with development settings

# 4. Start development services
docker-compose -f docker-compose.dev.yml up -d

# 5. Run database migrations
uv run alembic upgrade head

# 6. Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start frontend development server (in new terminal)
cd frontend
npm install
npm run dev
```

**Verification:**
- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] Database connection works
- [ ] Redis connection works
- [ ] S3 bucket access works

**Troubleshooting:**
- **Port conflicts**: Check if ports 8000, 3000, 5432, 6379 are available
- **Permission errors**: Ensure Docker daemon is running
- **Database errors**: Check PostgreSQL container logs
- **Environment variables**: Verify all required vars are set

---

### 1.2 Staging Deployment

**Prerequisites:**
- AWS credentials with deployment permissions
- GitHub Actions workflow configured
- Staging environment provisioned

**Automated Deployment (Recommended):**
```bash
# 1. Create release branch
git checkout -b release/v1.x.x
git push origin release/v1.x.x

# 2. GitHub Actions will automatically:
# - Run tests and security scans
# - Build Docker images
# - Deploy to staging environment
# - Run smoke tests

# 3. Monitor deployment
# Check GitHub Actions workflow status
# Verify staging health checks
```

**Manual Deployment (Emergency):**
```bash
# 1. Build and push Docker image
docker build -t facturx-express:staging .
docker tag facturx-express:staging 123456789.dkr.ecr.eu-west-1.amazonaws.com/facturx-express:staging
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/facturx-express:staging

# 2. Update ECS service
aws ecs update-service \
  --cluster facturx-staging \
  --service facturx-express-staging \
  --force-new-deployment

# 3. Monitor deployment
aws ecs wait services-stable \
  --cluster facturx-staging \
  --services facturx-express-staging
```

**Post-Deployment Verification:**
- [ ] Health check endpoint responds: `https://staging.facturx-express.com/health`
- [ ] Database migrations applied successfully
- [ ] All services are running
- [ ] Monitoring dashboards show green status
- [ ] Generate test invoice to verify core functionality

---

### 1.3 Production Deployment

**Prerequisites:**
- Staging deployment successful
- All tests passing
- Security scan clean
- Change approval obtained
- Rollback plan prepared

**Deployment Process:**
```bash
# 1. Create production release
git checkout main
git merge release/v1.x.x
git tag v1.x.x
git push origin main --tags

# 2. Manual approval in GitHub Actions
# Navigate to Actions tab and approve production deployment

# 3. Monitor deployment progress
# Watch GitHub Actions workflow
# Monitor AWS CloudWatch dashboards
# Check application logs

# 4. Verify deployment
curl -f https://api.facturx-express.com/health
# Run production smoke tests
```

**Rollback Procedure (if needed):**
```bash
# 1. Immediate rollback
aws ecs update-service \
  --cluster facturx-prod \
  --service facturx-express-prod \
  --task-definition facturx-express-prod:PREVIOUS_REVISION

# 2. Database rollback (if schema changes)
# Only if safe to do so - coordinate with team
uv run alembic downgrade -1

# 3. Notify stakeholders
# Send incident notification
# Update status page
```

---

## Monitoring & Alerting

### 2.1 Health Check Monitoring

**Automated Health Checks:**
```bash
# Application health check
curl -f https://api.facturx-express.com/health

# Database connectivity
curl -f https://api.facturx-express.com/health/db

# External services
curl -f https://api.facturx-express.com/health/dependencies
```

**Manual Health Verification:**
1. **Application Status:**
   - [ ] All ECS tasks running
   - [ ] Load balancer healthy targets
   - [ ] Auto-scaling groups within limits

2. **Database Status:**
   - [ ] RDS instance available
   - [ ] Connection pool not exhausted
   - [ ] No long-running queries

3. **External Dependencies:**
   - [ ] S3 bucket accessible
   - [ ] Redis cluster responsive
   - [ ] Email service operational

**Alert Thresholds:**
- **Critical**: Health check fails for > 2 minutes
- **Warning**: Response time > 5 seconds
- **Info**: Deployment notifications

---

### 2.2 Performance Monitoring

**Key Metrics to Monitor:**

1. **Application Metrics:**
   ```
   - Request rate (requests/second)
   - Response time (95th percentile)
   - Error rate (4xx/5xx responses)
   - Invoice generation time
   - Validation success rate
   ```

2. **Infrastructure Metrics:**
   ```
   - CPU utilization (< 80%)
   - Memory usage (< 85%)
   - Disk usage (< 90%)
   - Network I/O
   - Database connections
   ```

3. **Business Metrics:**
   ```
   - Invoices generated per hour
   - User registration rate
   - API usage by endpoint
   - Revenue metrics
   ```

**Grafana Dashboard URLs:**
- Application Overview: `https://grafana.company.com/d/app-overview`
- Infrastructure: `https://grafana.company.com/d/infrastructure`
- Business Metrics: `https://grafana.company.com/d/business`

**Performance Alert Rules:**
```yaml
# High response time
- alert: HighResponseTime
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 3
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High response time detected"

# High error rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
```

---

## Incident Response

### 3.1 Incident Classification

**Severity Levels:**

**P0 - Critical (< 15 min response)**
- Complete service outage
- Data loss or corruption
- Security breach
- Payment processing failure

**P1 - High (< 1 hour response)**
- Partial service degradation
- Performance issues affecting users
- Non-critical feature failures

**P2 - Medium (< 4 hours response)**
- Minor bugs not affecting core functionality
- Documentation issues
- Non-urgent feature requests

**P3 - Low (< 24 hours response)**
- Cosmetic issues
- Enhancement requests
- General questions

---

### 3.2 Incident Response Procedures

**P0 Critical Incident Response:**

1. **Immediate Response (0-15 minutes):**
   ```bash
   # 1. Acknowledge alert
   # 2. Join incident channel: #incident-response
   # 3. Assess impact and scope
   # 4. Implement immediate mitigation if possible
   
   # Quick mitigation options:
   # - Scale up resources
   aws ecs update-service --cluster facturx-prod --service facturx-express-prod --desired-count 10
   
   # - Enable maintenance mode
   aws elbv2 modify-target-group --target-group-arn arn:aws:... --health-check-path /maintenance
   
   # - Rollback to previous version
   aws ecs update-service --cluster facturx-prod --service facturx-express-prod --task-definition facturx-express-prod:PREVIOUS
   ```

2. **Investigation (15-60 minutes):**
   ```bash
   # Check application logs
   aws logs tail /aws/ecs/facturx-express --follow
   
   # Check infrastructure metrics
   # Navigate to CloudWatch dashboards
   
   # Check database performance
   aws rds describe-db-instances --db-instance-identifier facturx-prod
   
   # Check external dependencies
   curl -I https://api.stripe.com/v1
   ```

3. **Communication:**
   - Update status page: `https://status.facturx-express.com`
   - Notify stakeholders via Slack
   - Send customer communication if needed

4. **Resolution & Post-Mortem:**
   - Implement permanent fix
   - Document incident in post-mortem template
   - Schedule post-mortem meeting within 48 hours

---

### 3.3 Common Incident Scenarios

**Scenario 1: High Response Times**
```bash
# 1. Check current load
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Sum

# 2. Scale up if needed
aws ecs update-service \
  --cluster facturx-prod \
  --service facturx-express-prod \
  --desired-count 8

# 3. Check database performance
# Look for slow queries in RDS Performance Insights

# 4. Check Redis cache hit rate
redis-cli info stats | grep keyspace
```

**Scenario 2: Database Connection Issues**
```bash
# 1. Check RDS status
aws rds describe-db-instances --db-instance-identifier facturx-prod

# 2. Check connection pool
# Look at application metrics for connection pool exhaustion

# 3. Restart application if needed
aws ecs update-service \
  --cluster facturx-prod \
  --service facturx-express-prod \
  --force-new-deployment

# 4. Check for long-running queries
# Connect to database and run:
# SELECT * FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

**Scenario 3: Invoice Generation Failures**
```bash
# 1. Check validation service status
curl -f https://api.facturx-express.com/health/validation

# 2. Check S3 bucket permissions
aws s3 ls s3://facturx-invoices-prod/

# 3. Test invoice generation manually
curl -X POST https://api.facturx-express.com/api/invoices \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Test", "amount": 100}'

# 4. Check PDF generation service
# Look at WeasyPrint and factur-x library logs
```

---

## Backup & Recovery

### 4.1 Database Backup Procedures

**Automated Backups:**
- RDS automated backups: 7-day retention
- Point-in-time recovery enabled
- Cross-region backup replication

**Manual Backup Creation:**
```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier facturx-prod \
  --db-snapshot-identifier facturx-prod-manual-$(date +%Y%m%d-%H%M%S)

# Verify snapshot creation
aws rds describe-db-snapshots \
  --db-instance-identifier facturx-prod \
  --snapshot-type manual
```

**Database Recovery:**
```bash
# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier facturx-prod \
  --target-db-instance-identifier facturx-prod-recovery \
  --restore-time 2024-01-01T12:00:00.000Z

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier facturx-prod-recovery \
  --db-snapshot-identifier facturx-prod-snapshot-20240101
```

---

### 4.2 File Storage Backup

**S3 Backup Configuration:**
- Versioning enabled
- Cross-region replication
- Lifecycle policies for cost optimization

**Manual File Recovery:**
```bash
# List object versions
aws s3api list-object-versions \
  --bucket facturx-invoices-prod \
  --prefix invoices/2024/01/

# Restore specific version
aws s3api copy-object \
  --copy-source facturx-invoices-prod/invoices/2024/01/invoice-123.pdf?versionId=VERSION_ID \
  --bucket facturx-invoices-prod \
  --key invoices/2024/01/invoice-123.pdf
```

---

## Security Operations

### 5.1 Security Monitoring

**Daily Security Checks:**
```bash
# 1. Check for failed login attempts
aws logs filter-log-events \
  --log-group-name /aws/ecs/facturx-express \
  --filter-pattern "[timestamp, request_id, level=\"ERROR\", message=\"Authentication failed\"]"

# 2. Review API rate limiting logs
aws logs filter-log-events \
  --log-group-name /aws/ecs/facturx-express \
  --filter-pattern "[timestamp, request_id, level=\"WARNING\", message=\"Rate limit exceeded\"]"

# 3. Check for unusual API usage patterns
# Review CloudWatch metrics for API endpoints
```

**Security Incident Response:**
1. **Suspected Breach:**
   - Immediately rotate all API keys and secrets
   - Enable additional logging
   - Block suspicious IP addresses
   - Notify security team and legal

2. **DDoS Attack:**
   ```bash
   # Enable AWS Shield Advanced if not already active
   # Configure rate limiting at CloudFront level
   # Block malicious IPs using WAF rules
   ```

---

### 5.2 Certificate Management

**SSL Certificate Renewal:**
```bash
# Check certificate expiration
aws acm list-certificates --region eu-west-1

# Request new certificate (if needed)
aws acm request-certificate \
  --domain-name facturx-express.com \
  --subject-alternative-names *.facturx-express.com \
  --validation-method DNS
```

---

## Performance Tuning

### 6.1 Database Optimization

**Query Performance Analysis:**
```sql
-- Find slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename = 'invoices';

-- Analyze table statistics
ANALYZE invoices;
```

**Index Optimization:**
```sql
-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_invoices_user_created 
ON invoices(user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_invoices_status 
ON invoices(status) WHERE status IN ('pending', 'processing');
```

---

### 6.2 Application Performance Tuning

**Memory Optimization:**
```python
# Monitor memory usage
import psutil
import gc

def log_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
    
# Force garbage collection after heavy operations
gc.collect()
```

**Caching Strategy:**
```python
# Redis caching for frequently accessed data
import redis
from functools import wraps

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## Compliance Operations

### 7.1 EN 16931 Compliance Monitoring

**Daily Compliance Checks:**
```bash
# Check validation success rate
aws logs filter-log-events \
  --log-group-name /aws/ecs/facturx-express \
  --filter-pattern "[timestamp, request_id, level=\"INFO\", message=\"Validation completed\", status]" \
  --start-time $(date -d '1 day ago' +%s)000

# Generate compliance report
python scripts/generate_compliance_report.py --date $(date +%Y-%m-%d)
```

**Compliance Audit Preparation:**
1. **Data Collection:**
   - Export all validation logs
   - Generate invoice samples
   - Document validation procedures

2. **Evidence Package:**
   - Validation test results
   - System architecture documentation
   - Security controls documentation
   - Incident response logs

---

### 7.2 GDPR Compliance Operations

**Data Subject Requests:**
```bash
# Data export for user
python scripts/export_user_data.py --user-id 12345 --output gdpr_export.json

# Data deletion (right to be forgotten)
python scripts/delete_user_data.py --user-id 12345 --confirm

# Data portability
python scripts/export_user_invoices.py --user-id 12345 --format pdf
```

**Data Retention Management:**
```bash
# Archive old data (6+ years for invoices)
python scripts/archive_old_data.py --older-than 2190  # 6 years in days

# Clean up temporary files
find /tmp -name "*.pdf" -mtime +1 -delete
```

---

## Emergency Contacts

**On-Call Rotation:**
- Primary: [Name] - [Phone] - [Email]
- Secondary: [Name] - [Phone] - [Email]
- Escalation: [Manager] - [Phone] - [Email]

**External Contacts:**
- AWS Support: [Case URL]
- Security Team: security@company.com
- Legal Team: legal@company.com
- Customer Support: support@facturx-express.com

**Communication Channels:**
- Slack: #incident-response
- Status Page: https://status.facturx-express.com
- Monitoring: https://grafana.company.com

---

**Document Owner:** DevOps Team  
**Last Updated:** $(date)  
**Next Review:** Monthly  
**Emergency Updates:** As needed during incidents