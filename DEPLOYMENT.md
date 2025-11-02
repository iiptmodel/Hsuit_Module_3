# Deployment Guide

## Production Deployment Options

### Option 1: Deploy to Azure (Recommended)

#### Prerequisites
- Azure account
- Azure CLI installed
- Docker installed

#### Step 1: Create Azure Resources

```powershell
# Login to Azure
az login

# Create resource group
az group create --name medanalysis-rg --location eastus

# Create App Service Plan (B2 or higher for GPU support)
az appservice plan create `
    --name medanalysis-plan `
    --resource-group medanalysis-rg `
    --sku B2 `
    --is-linux

# Create Web App
az webapp create `
    --resource-group medanalysis-rg `
    --plan medanalysis-plan `
    --name medanalysis-app `
    --runtime "PYTHON:3.11"
```

#### Step 2: Configure Environment Variables

```powershell
# Set Neon database connection
az webapp config appsettings set `
    --resource-group medanalysis-rg `
    --name medanalysis-app `
    --settings DATABASE_URL="your-neon-connection-string"

# Set secret key
az webapp config appsettings set `
    --resource-group medanalysis-rg `
    --name medanalysis-app `
    --settings SECRET_KEY="your-generated-secret"
```

#### Step 3: Deploy Application

```powershell
# Deploy from Git
az webapp deployment source config `
    --name medanalysis-app `
    --resource-group medanalysis-rg `
    --repo-url https://github.com/iiptmodel/Hsuit_Module_3 `
    --branch main
```

---

### Option 2: Deploy to Railway

#### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

#### Step 2: Deploy from GitHub

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose `iiptmodel/Hsuit_Module_3`
4. Railway will auto-detect Python and start deployment

#### Step 3: Add Neon Database

1. In Railway dashboard, click **"New"** → **"Database"** → **"PostgreSQL"**
2. OR connect existing Neon database:
   - Go to Variables tab
   - Add `DATABASE_URL` with your Neon connection string

#### Step 4: Configure Environment Variables

Add these in Railway Variables:
```
DATABASE_URL=your-neon-connection-string
SECRET_KEY=your-generated-secret
HF_HOME=/app/models
TRANSFORMERS_CACHE=/app/models/transformers
```

#### Step 5: Access Application

Your app will be available at: `https://your-app.up.railway.app`

---

### Option 3: Deploy to Render

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

#### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repository: `iiptmodel/Hsuit_Module_3`
3. Configure:
   - **Name**: medanalysis
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 3: Add Environment Variables

In Environment tab, add:
```
DATABASE_URL=your-neon-connection-string
SECRET_KEY=your-generated-secret
PYTHON_VERSION=3.11
```

#### Step 4: Select Instance Type

- **Free tier**: Limited (not recommended for AI models)
- **Starter**: $7/month - Good for testing
- **Standard**: $25/month - Recommended for production

---

### Option 4: Docker Deployment

#### Create Dockerfile

```dockerfile
# d:\Prushal\Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p media/audio media/reports models

# Download models (optional - can be volume mounted)
# RUN python download_models.py

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run

```powershell
# Build image
docker build -t medanalysis .

# Run container
docker run -d `
    -p 8000:8000 `
    -e DATABASE_URL="your-neon-connection" `
    -e SECRET_KEY="your-secret" `
    -v ${PWD}/models:/app/models `
    --name medanalysis-app `
    medanalysis
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - HF_HOME=/app/models
    volumes:
      - ./models:/app/models
      - ./media:/app/media
    restart: unless-stopped
```

Run with:
```powershell
docker-compose up -d
```

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use HTTPS (SSL certificate)
- [ ] Enable CORS with specific allowed origins
- [ ] Set up rate limiting
- [ ] Enable database connection pooling
- [ ] Use environment variables (never hardcode secrets)

### Database

- [ ] Use Neon or managed PostgreSQL (not SQLite)
- [ ] Enable SSL mode (`?sslmode=require`)
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Add database monitoring

### Performance

- [ ] Use multiple Uvicorn workers: `--workers 4`
- [ ] Enable response compression
- [ ] Set up CDN for static files
- [ ] Cache model predictions
- [ ] Use GPU if available
- [ ] Implement request queuing for model inference

### Monitoring

- [ ] Set up logging (CloudWatch, Datadog, etc.)
- [ ] Add error tracking (Sentry)
- [ ] Monitor GPU/CPU usage
- [ ] Track API response times
- [ ] Set up uptime monitoring
- [ ] Configure alerts

### Models

- [ ] Pre-download models before deployment
- [ ] Mount models as persistent volume
- [ ] Consider model quantization for smaller size
- [ ] Set up model versioning
- [ ] Monitor model performance

---

## Environment-Specific Configurations

### Development (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost/medanalysis_dev
SECRET_KEY=dev-secret-key-not-secure
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### Production (.env.production)
```env
DATABASE_URL=postgresql://user:pass@neon-host/medanalysis_prod?sslmode=require
SECRET_KEY=super-secure-production-key-32-chars-min
LOG_LEVEL=INFO
ENVIRONMENT=production
CORS_ORIGINS=["https://yourdomain.com"]
```

---

## Scaling Considerations

### Horizontal Scaling

```python
# Use Gunicorn with multiple Uvicorn workers
gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### Load Balancing

- Use Nginx or cloud load balancer
- Sticky sessions for file uploads
- Health check endpoint: `/api/v1/health`

### Caching

```python
# Add Redis for caching model results
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="medanalysis-cache")
```

---

## Cost Estimation (Monthly)

### Minimal Setup (Development)
- **Neon Database**: Free tier (0.5GB storage)
- **Railway/Render**: Free tier or $7/month
- **Total**: $0 - $7/month

### Production Setup (100-500 users)
- **Neon Database**: $19/month (Pro plan)
- **Railway Standard**: $25/month
- **OR Azure App Service B2**: ~$55/month
- **Total**: $44 - $74/month

### High Traffic (1000+ users)
- **Neon Database**: $69/month (Scale plan)
- **Azure App Service P2V2**: ~$150/month
- **CDN**: ~$10/month
- **Monitoring**: ~$20/month
- **Total**: ~$249/month

---

## Troubleshooting Production Issues

### Models Not Loading

```python
# Add to startup event
import logging
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def check_models():
    try:
        from app.services import summarizer_service
        logger.info("✅ Models loaded successfully")
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        raise
```

### Database Connection Pool Exhausted

```python
# In database.py, increase pool size
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Increase from default 5
    max_overflow=10
)
```

### Out of Memory

```python
# Enable model quantization
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    load_in_8bit=True,  # Reduces memory by ~50%
    device_map="auto"
)
```

---

## Support & Maintenance

- **Logs Location**: `/var/log/medanalysis/`
- **Health Check**: `GET /api/v1/health`
- **Metrics**: `GET /api/v1/metrics`
- **Documentation**: `GET /docs` (Swagger UI)

For issues, check:
1. Application logs
2. Database connection status
3. Model loading status
4. Disk space for models (~15GB needed)
5. Memory usage (16GB+ recommended)
