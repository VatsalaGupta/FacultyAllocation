# Docker Quick Start Guide

## Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- 2GB free disk space
- Port 8501 available

## Option 1: Docker Run (Simple)

### Build the Image
```bash
docker build -t faculty-allocation .
```

### Run the Container
```bash
docker run -p 8501:8501 faculty-allocation
```

### Access the App
Open browser: http://localhost:8501

### Stop the Container
Press `Ctrl+C` in the terminal

## Option 2: Docker Compose (Recommended)

### Start the Application
```bash
docker-compose up
```

### Run in Background
```bash
docker-compose up -d
```

### Stop the Application
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

## Common Commands

### List Running Containers
```bash
docker ps
```

### Stop a Container
```bash
docker stop <container-id>
```

### Remove a Container
```bash
docker rm <container-id>
```

### Remove the Image
```bash
docker rmi faculty-allocation
```

### Rebuild from Scratch
```bash
docker-compose build --no-cache
docker-compose up
```

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8501 failed: port is already allocated`

**Solution 1:** Stop the other application using port 8501
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill
```

**Solution 2:** Use a different port
```bash
docker run -p 8502:8501 faculty-allocation
```
Then access at: http://localhost:8502

### Container Won't Start

**Check logs:**
```bash
docker logs <container-id>
```

**Common issues:**
- Missing dependencies → Rebuild image
- Port conflict → Change port
- Out of memory → Increase Docker memory limit

### Build Fails

**Clear Docker cache:**
```bash
docker system prune -a
docker build --no-cache -t faculty-allocation .
```

### Slow Performance

**Increase Docker resources:**
1. Open Docker Desktop
2. Settings → Resources
3. Increase CPU and Memory
4. Apply & Restart

## Production Deployment

### Using Docker Hub

1. **Tag the image:**
```bash
docker tag faculty-allocation yourusername/faculty-allocation:latest
```

2. **Push to Docker Hub:**
```bash
docker login
docker push yourusername/faculty-allocation:latest
```

3. **Pull and run on server:**
```bash
docker pull yourusername/faculty-allocation:latest
docker run -d -p 8501:8501 --restart=always yourusername/faculty-allocation:latest
```

### Using Docker Compose in Production

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  faculty-allocation:
    image: yourusername/faculty-allocation:latest
    ports:
      - "80:8501"
    restart: always
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
```

Run:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

You can customize the application with environment variables:

```bash
docker run -p 8501:8501 \
  -e STREAMLIT_SERVER_PORT=8501 \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  faculty-allocation
```

## Persistent Data

To save uploaded files and outputs:

```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  faculty-allocation
```

Windows (PowerShell):
```powershell
docker run -p 8501:8501 `
  -v ${PWD}/data:/app/data `
  faculty-allocation
```

## Health Check

Check if the application is healthy:
```bash
curl http://localhost:8501/_stcore/health
```

Should return: `{"status": "ok"}`

## Best Practices

1. ✅ Always use `docker-compose` for easier management
2. ✅ Use version tags instead of `latest` in production
3. ✅ Set `restart: unless-stopped` for automatic recovery
4. ✅ Monitor logs regularly: `docker-compose logs -f`
5. ✅ Back up important data outside containers
6. ✅ Update images regularly for security patches

## Need Help?

- Check logs: `docker-compose logs`
- Verify health: `curl http://localhost:8501/_stcore/health`
- Rebuild: `docker-compose build --no-cache`
- Ask for help: Open an issue on GitHub

---

**Happy Containerizing! 🐳**
