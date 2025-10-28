# 🚀 Docker Quick Start

## 🎯 Deploy in 30 Seconds

```bash
./docker-deploy.sh
```

That's it! The script does everything automatically.

## 📋 Manual Deployment (3 Steps)

```bash
# 1. Setup environment
cp .env.docker.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Start
docker-compose up -d

# 3. Access
open http://localhost:8000
```

## 🔧 Essential Commands

| Action | Command |
|--------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose stop` |
| Restart | `docker-compose restart` |
| Logs | `docker-compose logs -f` |
| Status | `docker-compose ps` |
| Remove | `docker-compose down` |
| Rebuild | `docker-compose up -d --build` |

## 🌐 Access Points

- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🐛 Troubleshooting

**Problem**: Port 8000 in use
```bash
lsof -i :8000
# Kill the process or change port in docker-compose.yml
```

**Problem**: Container won't start
```bash
docker-compose logs chatbot
```

**Problem**: Need to rebuild
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Full Documentation

See `DOCKER.md` for complete guide.

---

**Ready to deploy? Run: `./docker-deploy.sh` 🐳**
