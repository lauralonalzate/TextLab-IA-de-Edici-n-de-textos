# TextLab Backend - Production Deployment Guide

This guide covers deploying TextLab backend to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Docker Compose Deployment (VPS)](#docker-compose-deployment-vps)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Health Checks and Monitoring](#health-checks-and-monitoring)
7. [Backups and Maintenance](#backups-and-maintenance)
8. [Scaling Recommendations](#scaling-recommendations)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured (for SSL)
- SSH access to VPS (for VPS deployment)
- Cloud provider account (for cloud deployment)
- Basic knowledge of Linux, Docker, and networking

## Deployment Options

### Option 1: VPS with Docker Compose
Best for: Small to medium deployments, single server setup
- Full control over infrastructure
- Cost-effective
- Requires manual maintenance

### Option 2: Cloud Platforms (Render, Railway, Fly.io)
Best for: Quick deployment, managed infrastructure
- Easy setup
- Automatic scaling (some platforms)
- Less control over infrastructure

### Option 3: Kubernetes
Best for: Large scale, high availability
- Auto-scaling
- Self-healing
- Complex setup

## Docker Compose Deployment (VPS)

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Clone Repository

```bash
git clone <your-repo-url> textlab-backend
cd textlab-backend
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env.production

# Edit with your values
nano .env.production
```

Required variables for production:

```bash
# Database
POSTGRES_USER=textlab_prod
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=textlab_prod

# Redis
REDIS_PASSWORD=<strong-redis-password>

# Security
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256

# CORS (replace with your frontend URL)
CORS_ORIGINS=https://app.textlab.com,https://www.textlab.com

# Domain
DOMAIN_NAME=api.textlab.com
CERTBOT_EMAIL=admin@textlab.com

# Production settings
ENVIRONMENT=production
DEBUG=false
TRUST_PROXY=true

# Gunicorn workers (adjust based on CPU cores)
GUNICORN_WORKERS=4

# Celery
CELERY_WORKER_CONCURRENCY=4

# Storage (choose one)
STORAGE_BACKEND=local  # or s3
STORAGE_PATH=/app/exports

# If using S3
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# AWS_REGION=us-east-1
# S3_BUCKET_NAME=textlab-exports
```

### Step 4: Create Nginx Configuration

```bash
# Create nginx directories
mkdir -p nginx/conf.d nginx/ssl nginx/logs

# The nginx configuration files are already in the repo
# Edit nginx/conf.d/textlab.conf and replace ${DOMAIN_NAME} with your domain
sed -i 's/${DOMAIN_NAME}/api.textlab.com/g' nginx/conf.d/textlab.conf
```

### Step 5: Initial SSL Certificate (Let's Encrypt)

```bash
# Start services without SSL first
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d nginx

# Request certificate
docker-compose -f docker-compose.prod.yml --env-file .env.production run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email admin@textlab.com --agree-tos --no-eff-email -d api.textlab.com

# Update nginx config to use SSL and restart
docker-compose -f docker-compose.prod.yml --env-file .env.production restart nginx
```

### Step 6: Deploy Application

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Run database migrations
docker-compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head

# Check logs
docker-compose -f docker-compose.prod.yml --env-file .env.production logs -f
```

### Step 7: Verify Deployment

```bash
# Check health endpoint
curl https://api.textlab.com/health

# Check readiness
curl https://api.textlab.com/ready

# Check service status
docker-compose -f docker-compose.prod.yml --env-file .env.production ps
```

### Step 8: Setup SSL Auto-Renewal

```bash
# Add cron job for SSL renewal
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /path/to/textlab-backend && docker-compose -f docker-compose.prod.yml --env-file .env.production run --rm certbot renew && docker-compose -f docker-compose.prod.yml --env-file .env.production restart nginx
```

## Cloud Platform Deployment

### Render.com

1. **Create New Web Service**
   - Connect your GitHub repository
   - Select "Docker" as environment
   - Build command: `docker build -t textlab-backend .`
   - Start command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

2. **Environment Variables**
   - Add all variables from `.env.example`
   - Use Render's managed PostgreSQL and Redis

3. **Background Workers**
   - Create separate "Background Worker" service
   - Command: `celery -A app.celery_app worker --loglevel=info`

### Railway.app

1. **Deploy from GitHub**
   - Connect repository
   - Railway auto-detects Dockerfile

2. **Add Services**
   - Add PostgreSQL service
   - Add Redis service
   - Link to your app

3. **Environment Variables**
   - Set in Railway dashboard
   - Use Railway's service URLs for DATABASE_URL and REDIS_URL

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and create app
fly auth login
fly launch

# Set secrets
fly secrets set SECRET_KEY=<your-secret>
fly secrets set DATABASE_URL=<postgres-url>
fly secrets set REDIS_URL=<redis-url>

# Deploy
fly deploy
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm 3.x installed (optional)

### Using Helm

Create `helm/values.yaml`:

```yaml
replicaCount: 3

image:
  repository: textlab-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.textlab.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: textlab-tls
      hosts:
        - api.textlab.com

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

postgresql:
  enabled: true
  auth:
    postgresPassword: "changeme"
    database: "textlab"

redis:
  enabled: true
  auth:
    enabled: true
    password: "changeme"

celery:
  workers: 2
  concurrency: 4
```

Deploy with Helm:

```bash
# Install chart
helm install textlab ./helm

# Or use a public chart template
helm create textlab
# Edit values.yaml and templates
helm install textlab ./textlab
```

### Manual Kubernetes Deployment

See `k8s/` directory for example manifests:

```bash
# Apply namespace
kubectl apply -f k8s/namespace.yaml

# Apply secrets
kubectl create secret generic textlab-secrets \
  --from-env-file=.env.production \
  -n textlab

# Apply configmaps
kubectl apply -f k8s/configmap.yaml

# Apply deployments
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/celery-worker.yaml
kubectl apply -f k8s/celery-beat.yaml

# Apply services
kubectl apply -f k8s/services.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

## Health Checks and Monitoring

### Health Endpoints

- **Liveness**: `GET /health`
  - Returns: `{"status": "ok", "service": "textlab-api"}`
  - Use for: Container restart on failure

- **Readiness**: `GET /ready`
  - Returns: `{"status": "ready", "checks": {"database": "ok", "redis": "ok"}}`
  - Use for: Traffic routing, load balancer health checks

### Monitoring Setup

#### Prometheus (Optional)

Add to `docker-compose.prod.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

#### Log Aggregation

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Export logs
docker-compose -f docker-compose.prod.yml logs > logs.txt
```

## Backups and Maintenance

### Database Backups

Automatic backups are configured in `docker-compose.prod.yml`:

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > backup-$(date +%Y%m%d).sql.gz

# Restore backup
gunzip < backup-20240101.sql.gz | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB
```

### Storage Backups

If using local storage:

```bash
# Backup exports directory
tar -czf exports-backup-$(date +%Y%m%d).tar.gz exports/
```

If using S3, enable S3 versioning and lifecycle policies.

### Maintenance Tasks

```bash
# Update application
git pull
docker-compose -f docker-compose.prod.yml --env-file .env.production build
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# Run migrations
docker-compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head

# Restart services
docker-compose -f docker-compose.prod.yml --env-file .env.production restart

# Scale workers
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --scale celery-worker=4
```

## Scaling Recommendations

### Horizontal Scaling

1. **Backend Workers**
   ```bash
   # Scale backend instances
   docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --scale backend=3
   ```

2. **Celery Workers**
   ```bash
   # Scale celery workers
   docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --scale celery-worker=4
   ```

3. **Load Balancing**
   - Update `nginx/conf.d/textlab.conf` with multiple backend servers
   - Use external load balancer (AWS ALB, GCP LB) for cloud deployments

### Vertical Scaling

- Increase `GUNICORN_WORKERS` based on CPU cores
- Adjust `CELERY_WORKER_CONCURRENCY`
- Increase container memory limits

### Database Scaling

- Use managed PostgreSQL (AWS RDS, GCP Cloud SQL, Azure Database)
- Enable connection pooling (PgBouncer)
- Read replicas for read-heavy workloads

### Redis Scaling

- Use managed Redis (AWS ElastiCache, GCP Memorystore)
- Redis Cluster for high availability
- Separate Redis instances for cache and Celery

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database logs
   docker-compose -f docker-compose.prod.yml logs postgres
   
   # Test connection
   docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; engine.connect()"
   ```

2. **Redis Connection Errors**
   ```bash
   # Check Redis
   docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
   ```

3. **SSL Certificate Issues**
   ```bash
   # Renew certificate manually
   docker-compose -f docker-compose.prod.yml run --rm certbot renew
   ```

4. **High Memory Usage**
   ```bash
   # Check container stats
   docker stats
   
   # Restart workers to clear memory
   docker-compose -f docker-compose.prod.yml restart celery-worker
   ```

### Performance Tuning

1. **Database**
   - Enable connection pooling
   - Add indexes for frequently queried columns
   - Analyze query performance

2. **Application**
   - Adjust Gunicorn workers: `workers = (2 * CPU) + 1`
   - Enable response caching
   - Optimize database queries

3. **Nginx**
   - Enable gzip compression
   - Configure caching headers
   - Tune worker processes

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (only allow 80, 443)
- [ ] Use managed database (if possible)
- [ ] Enable database backups
- [ ] Set up log monitoring
- [ ] Regular security updates
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Use non-root user in containers
- [ ] Scan images for vulnerabilities

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review health endpoints: `/health` and `/ready`
- Check service status: `docker-compose ps`

