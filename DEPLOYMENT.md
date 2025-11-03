# Production Deployment Guide

## Overview

This guide covers deploying the Medical Report Analysis System to production environments with proper security, scalability, and monitoring.

## 🚀 Deployment Options

### Option 1: Railway (Recommended for Quick Deployment)

**Best for**: Small to medium applications, rapid prototyping

#### Prerequisites
- Railway account (free tier available)
- GitHub repository

#### Steps

1. **Connect Repository**
   ```bash
   # Push code to GitHub
   git add .
   git commit -m "Production ready"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository

3. **Configure Environment Variables**
   ```env
   DATABASE_URL=postgresql://... # Railway provides this
   SECRET_KEY=your-generated-secret-key
   ENVIRONMENT=production
   ```

4. **Database Setup**
   - Railway automatically provisions PostgreSQL
   - Copy the `DATABASE_URL` from Railway dashboard

5. **Deploy**
   - Railway auto-deploys on push
   - Monitor logs in Railway dashboard

**Cost**: $5-15/month
**GPU**: No (use Render/AWS for GPU)

---

### Option 2: Render (Good for GPU Support)

**Best for**: Applications needing GPU acceleration

#### Prerequisites
- Render account
- GPU-enabled instance (paid plans)

#### Steps

1. **Create Web Service**
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect GitHub repository

2. **Service Configuration**
   ```yaml
   # render.yaml
   services:
     - type: web
       name: med-analyzer
       env: python
       buildCommand: pip install -r requirements.txt && python download_models.py
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           value: postgresql://...
         - key: SECRET_KEY
           value: your-secret
         - key: ENVIRONMENT
           value: production
   ```

3. **GPU Instance Selection**
   - Choose "GPU" instance type ($25-100/month)
   - Minimum: RTX 3060 equivalent

**Cost**: $25-100/month
**GPU**: Yes (NVIDIA GPUs)

---

### Option 3: AWS EC2 with GPU

**Best for**: Full control, HIPAA compliance, enterprise deployments

#### Prerequisites
- AWS account
- GPU instance (P3, G4dn, G5 series)

#### Steps

1. **Launch EC2 Instance**
   ```bash
   # Instance type recommendations:
   # g4dn.xlarge: 1 GPU, 16GB VRAM (~$0.50/hour)
   # g5.xlarge: 1 GPU, 24GB VRAM (~$1.00/hour)
   # p3.2xlarge: 1 GPU, 16GB VRAM (~$3.00/hour)
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python 3.11
   sudo apt install python3.11 python3.11-venv -y

   # Install CUDA (if not pre-installed)
   wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
   sudo sh cuda_11.8.0_520.61.05_linux.run --no-opengl-libs
   ```

3. **Setup Application**
   ```bash
   # Clone repository
   git clone https://github.com/your-repo/med-analyzer.git
   cd med-analyzer

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

   # Download models
   python download_models.py
   ```

4. **Configure Environment**
   ```bash
   # Create .env file
   cat > .env << EOF
   DATABASE_URL=postgresql://user:pass@rds-endpoint/db
   SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   ENVIRONMENT=production
   EOF
   ```

5. **Setup Database (RDS)**
   - Create PostgreSQL RDS instance
   - Configure security groups
   - Enable SSL connections

6. **Run Application**
   ```bash
   # Use Gunicorn for production
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

7. **Setup Nginx (Optional)**
   ```nginx
   # /etc/nginx/sites-available/med-analyzer
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

**Cost**: $50-500/month (depending on instance)
**GPU**: Yes (various NVIDIA options)

---

### Option 4: Docker Containerization

**Best for**: Consistent deployments, Kubernetes orchestration

#### Dockerfile
```dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download models (optional: do at runtime for smaller image)
# RUN python download_models.py

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  med-analyzer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/db
      - SECRET_KEY=your-secret
    volumes:
      - ./models:/app/models
      - ./media:/app/media
    depends_on:
      - db
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=medanalyzer
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Build and Run
```bash
# Build image
docker build -t med-analyzer .

# Run locally
docker-compose up -d

# For GPU support
docker run --gpus all -p 8000:8000 med-analyzer
```

---

## 🔒 Security Configuration

### Environment Variables
```env
# Security
SECRET_KEY=your-super-secure-random-key-32-chars-min
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Application
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AI Models
HF_HOME=/app/models
TRANSFORMERS_CACHE=/app/models/transformers
```

### Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Should output something like:
# 8Xui6JgGpKS9X8K9Q8xNfK8KjGpKS9X8K9Q8xNfK8Kj
```

### Database Security
```sql
-- Create application user with limited permissions
CREATE USER medapp WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE medanalyzer TO medapp;
GRANT USAGE ON SCHEMA public TO medapp;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO medapp;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO medapp;

-- Enable Row Level Security (RLS) for multi-tenant support
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_reports ON reports FOR ALL USING (owner_id = current_user_id);
```

### SSL/TLS Configuration
```python
# In app/core/config.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    # ... other settings ...

    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if not v.startswith("postgresql://"):
            raise ValueError("Database URL must use postgresql:// scheme")
        if "sslmode=require" not in v:
            v += "?sslmode=require"
        return v
```

### CORS Configuration
```python
# In app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring & Logging

### Application Monitoring
```python
# Install: pip install prometheus-client
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def monitor_requests(request, call_next):
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    with REQUEST_LATENCY.labels(request.method, request.url.path).time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest())
```

### Health Checks
```python
# In app/main.py
@app.get("/health")
async def health_check():
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Check AI models
    try:
        model_status = "loaded" if summarizer_service._MODEL_AVAILABLE else "unavailable"
    except Exception:
        model_status = "error"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "ai_models": model_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Log Aggregation
```python
# Use structured logging
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

---

## 🔧 Performance Optimization

### GPU Optimization
```python
# In summarizer_service.py
import torch

# Enable CUDA optimizations
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Use mixed precision
with torch.cuda.amp.autocast():
    outputs = model.generate(**inputs)
```

### Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX idx_reports_owner_created ON reports(owner_id, created_at DESC);
CREATE INDEX idx_chat_sessions_created ON chat_sessions(created_at DESC);
CREATE INDEX idx_chat_messages_session_created ON chat_messages(session_id, created_at ASC);

-- Enable connection pooling
# In database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Caching
```python
# Install: pip install redis
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache AI model inferences
@redis_client.cache(expire=3600)
def cached_summarization(text: str) -> str:
    return generate_summary(text)
```

---

## 🚨 Backup & Recovery

### Database Backups
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Model Backups
```bash
# Backup models directory
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Restore
tar -xzf models_backup_20231201.tar.gz
```

### Disaster Recovery
1. **Spin up new instance**
2. **Restore database from backup**
3. **Restore models from backup**
4. **Update DNS/load balancer**
5. **Test application functionality**

---

## 📈 Scaling

### Horizontal Scaling
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: med-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: med-analyzer
  template:
    metadata:
      labels:
        app: med-analyzer
    spec:
      containers:
      - name: med-analyzer
        image: med-analyzer:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "8Gi"
            cpu: "2"
```

### Load Balancing
```nginx
upstream med_analyzer {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://med_analyzer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🧪 Testing Production Deployment

### Pre-deployment Checklist
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] SSL certificates installed
- [ ] DNS configured
- [ ] Firewall rules set
- [ ] Monitoring tools configured
- [ ] Backup scripts tested

### Post-deployment Tests
```bash
# Health check
curl https://your-domain.com/health

# API functionality
curl -X POST https://your-domain.com/api/v1/reports/upload-text \
  -H "Content-Type: application/json" \
  -d '{"text_content":"Test report","language":"en"}'

# Performance test
ab -n 100 -c 10 https://your-domain.com/health
```

---

## 🆘 Troubleshooting Production

### Common Issues

#### High Memory Usage
```bash
# Monitor memory
htop

# Check GPU memory
nvidia-smi

# Restart application
sudo systemctl restart med-analyzer
```

#### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check connection pool
# In database.py, reduce pool_size if needed
```

#### Model Loading Failures
```bash
# Clear model cache
rm -rf models/

# Re-download models
python download_models.py

# Check disk space
df -h
```

#### SSL Certificate Issues
```bash
# Test SSL
openssl s_client -connect your-domain.com:443

# Renew Let's Encrypt
certbot renew
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Monitor logs and metrics
- **Weekly**: Database backups, security updates
- **Monthly**: Performance reviews, dependency updates
- **Quarterly**: Model updates, security audits

### Emergency Contacts
- **Database Issues**: DBA team
- **Infrastructure**: DevOps team
- **Security**: Security team
- **Application**: Development team

### Documentation Updates
- Keep deployment docs current
- Document custom configurations
- Update troubleshooting guides
- Maintain change logs

---

**Last Updated**: November 2025
**Version**: 1.0.0
