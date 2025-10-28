# Docker Deployment Guide

This guide explains how to deploy the AI Chatbot using Docker and Docker Compose.

## 📋 Prerequisites

- **Docker Desktop** (includes Docker Engine and Docker Compose)
  - [Download for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Download for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Download for Linux](https://docs.docker.com/desktop/install/linux-install/)

- **API Keys**
  - OpenAI API key (required) - Get it from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Anthropic API key (optional) - Get it from [Anthropic Console](https://console.anthropic.com/)

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

1. **Run the deployment script:**
   ```bash
   ./docker-deploy.sh
   ```

   This script will:
   - Verify Docker installation
   - Create `.env` file from template
   - Build the Docker image
   - Start the containers
   - Perform health checks
   - Open the web UI in your browser

2. **Access the application:**
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Deployment

1. **Create environment file:**
   ```bash
   cp .env.docker.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4o-mini
   ```

3. **Build and start:**
   ```bash
   docker-compose up -d --build
   ```

4. **Check status:**
   ```bash
   docker-compose ps
   ```

## 🔧 Docker Commands

### Basic Operations

```bash
# Build the image
docker-compose build

# Start containers (detached mode)
docker-compose up -d

# Stop containers
docker-compose stop

# Start stopped containers
docker-compose start

# Restart containers
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

### Monitoring & Debugging

```bash
# View logs (follow mode)
docker-compose logs -f chatbot

# View last 100 lines of logs
docker-compose logs --tail=100 chatbot

# Check container status
docker-compose ps

# Execute commands in container
docker-compose exec chatbot /bin/bash

# Check resource usage
docker stats ai_chatbot
```

### Updating the Application

```bash
# Pull latest code from Git
git pull

# Rebuild and restart
docker-compose up -d --build

# Or use the no-cache option for complete rebuild
docker-compose build --no-cache
docker-compose up -d
```

## 📁 Docker Files Overview

### Dockerfile
Multi-stage build optimized for production:
- **Stage 1 (Builder)**: Installs build dependencies and Python packages
- **Stage 2 (Production)**: Minimal runtime image with only necessary files
- **Security**: Runs as non-root user
- **Health Check**: Built-in health monitoring

### docker-compose.yml
Orchestrates the application with:
- Port mapping (8000:8000)
- Environment variable injection
- Volume mounting for logs
- Automatic restart policy
- Health checks
- Network isolation

### .dockerignore
Excludes unnecessary files from Docker build context:
- Virtual environments
- Cache files
- Git history
- Documentation
- Tests

## 🌐 Networking

### Port Configuration

Default port: **8000**

To change the port, edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Host:Container
```

### Accessing from Other Machines

1. **Find your local IP:**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. **Access from other devices:**
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

3. **Important**: Ensure firewall allows incoming connections on port 8000

## 💾 Data Persistence

### Logs

Logs are persisted in `./logs` directory:
```yaml
volumes:
  - ./logs:/app/logs
```

To view logs:
```bash
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log
```

### Cost Tracking Data

Cost tracking uses in-memory storage. To persist across restarts, you could:
1. Add a database (PostgreSQL, Redis)
2. Mount a volume for data files
3. Use Docker volumes for state persistence

## 🔒 Security Best Practices

### 1. Environment Variables
```bash
# Never commit .env file
# Use .env.docker.example as template
echo ".env" >> .gitignore
```

### 2. API Keys
- Store in `.env` file (already in `.gitignore`)
- Use Docker secrets for production
- Rotate keys regularly

### 3. Network Security
```bash
# Limit container privileges
docker-compose exec --user appuser chatbot /bin/bash

# Use read-only filesystem where possible
# Scan images for vulnerabilities
docker scan ai_chatbot
```

### 4. Resource Limits

Add to `docker-compose.yml`:
```yaml
services:
  chatbot:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          memory: 1G
```

## 🐛 Troubleshooting

### Container won't start

1. **Check logs:**
   ```bash
   docker-compose logs chatbot
   ```

2. **Verify environment variables:**
   ```bash
   docker-compose config
   ```

3. **Check port availability:**
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

### Application returns errors

1. **Verify API key:**
   ```bash
   docker-compose exec chatbot env | grep API_KEY
   ```

2. **Test API connectivity:**
   ```bash
   docker-compose exec chatbot curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

### High memory usage

1. **Check stats:**
   ```bash
   docker stats ai_chatbot
   ```

2. **Restart container:**
   ```bash
   docker-compose restart chatbot
   ```

3. **Add memory limits** (see Security section)

### Build failures

1. **Clear Docker cache:**
   ```bash
   docker-compose build --no-cache
   ```

2. **Remove old images:**
   ```bash
   docker system prune -a
   ```

3. **Check disk space:**
   ```bash
   docker system df
   ```

## 🚢 Production Deployment

### Using Docker Hub

1. **Build and tag:**
   ```bash
   docker build -t yourusername/ai-chatbot:latest .
   docker push yourusername/ai-chatbot:latest
   ```

2. **Pull on server:**
   ```bash
   docker pull yourusername/ai-chatbot:latest
   docker run -d -p 8000:8000 --env-file .env yourusername/ai-chatbot:latest
   ```

### Using Cloud Platforms

**AWS ECS/Fargate:**
- Use ECR for image registry
- Configure task definitions
- Set up load balancer

**Google Cloud Run:**
```bash
gcloud run deploy ai-chatbot \
  --image gcr.io/PROJECT_ID/ai-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name ai-chatbot \
  --image yourusername/ai-chatbot:latest \
  --ports 8000
```

### Environment-Specific Configurations

Create separate compose files:

**docker-compose.prod.yml:**
```yaml
version: '3.8'
services:
  chatbot:
    image: yourusername/ai-chatbot:latest
    environment:
      - LOG_LEVEL=WARNING
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

Deploy:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### Health Checks

Built-in health check runs every 30 seconds:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' ai_chatbot
```

### Logging

View structured logs:
```bash
# All logs
docker-compose logs -f

# Filter by level
docker-compose logs | grep ERROR

# JSON format (if configured)
docker-compose logs --no-log-prefix | jq
```

### Cost Monitoring

Access cost tracking:
```bash
# Current costs
curl http://localhost:8000/v1/costs/latest

# Recent requests
curl http://localhost:8000/v1/costs/requests
```

## 🎯 Performance Optimization

### 1. Multi-stage Builds
Already implemented - reduces image size by ~50%

### 2. Layer Caching
Order Dockerfile commands from least to most frequently changed

### 3. Minimize Image Size
```bash
# Check image size
docker images | grep ai-chatbot

# Remove unnecessary files in Dockerfile
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
```

### 4. Use .dockerignore
Already configured to exclude unnecessary files

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)

## 💡 Tips

1. **Development Mode**: Uncomment volume mounts in `docker-compose.yml` to enable hot-reload
2. **Multiple Environments**: Use separate `.env` files (`.env.dev`, `.env.prod`)
3. **CI/CD**: Integrate with GitHub Actions, GitLab CI, or Jenkins
4. **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling
5. **Backup**: Regularly backup logs and configuration files

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Open an issue on GitHub
4. Check Docker Desktop dashboard for insights

---

**Ready to deploy? Run `./docker-deploy.sh` and you're live in minutes! 🚀**
