# Docker Deployment Instructions

## Local Development

### 1. Start Local Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f braindrive-document-ai

# Stop services
docker-compose down
```

### 2. Access Points (Local)
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Production Deployment

### 1. Prerequisites

**Generate API Keys:**
```bash
# Linux/macOS
./generate_keys.sh --both

# Windows
.\generate_keys.ps1 -Both
```

**Prepare Environment:**
```bash
# Copy template and edit
cp .env.production .env
# Edit .env with your actual values
```

**SSL Certificates:**
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/
```

### 2. Deploy Production Stack
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Access Points (Production)
- **API**: https://your-domain.com
- **Health Check**: https://your-domain.com/health (or http for load balancers)
- **Prometheus**: http://monitoring.your-domain.com/prometheus
- **Grafana**: http://monitoring.your-domain.com/grafana
- **Uptime Kuma**: http://your-domain.com:3001

### 4. Initial Setup

**Grafana Setup:**
1. Access Grafana at http://monitoring.your-domain.com/grafana
2. Login with admin / `${GRAFANA_PASSWORD}`
3. Configure Prometheus datasource: http://prometheus:9090
4. Import dashboards for FastAPI and system monitoring

**Prometheus Setup:**
1. Access Prometheus at http://monitoring.your-domain.com/prometheus
2. Verify targets are up in Status → Targets
3. Check metrics are being collected

### 5. Testing Production Deployment

**Test Authentication:**
```bash
# Should fail without API key
curl -X POST "https://your-domain.com/documents/upload" \
  -F "file=@test.pdf"

# Should succeed with API key
curl -X POST "https://your-domain.com/documents/upload" \
  -H "X-API-Key: your-api-key" \
  -F "file=@test.pdf"

# Health check
curl https://your-domain.com/health
```

## Environment Variables Reference

### Required Production Variables
```bash
# In .env file
DISABLE_AUTH=false
API_KEY=sk-your-generated-api-key
DOMAIN=your-domain.com
REDIS_PASSWORD=secure-password
GRAFANA_PASSWORD=secure-password
```

### SSL Certificate Setup
```bash
# Let's Encrypt example
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

## Scaling and Performance

### Scale Application Instances
```bash
# Scale to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale braindrive-document-ai=3
```

### Resource Monitoring
- **CPU/Memory**: View in Grafana dashboards
- **Request Rate**: Check Nginx access logs
- **Response Times**: Monitor in Prometheus metrics

### Performance Tuning
1. Adjust `MAX_CONCURRENT_PROCESSES` based on CPU cores
2. Tune Nginx worker processes
3. Configure Redis memory limits
4. Set appropriate upload file size limits

## Backup and Maintenance

### Backup Data Volumes
```bash
# Create backup
docker run --rm -v braindrive_uploads_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz /data

# Restore backup
docker run --rm -v braindrive_uploads_data:/data -v $(pwd):/backup alpine tar xzf /backup/uploads-backup.tar.gz -C /
```
