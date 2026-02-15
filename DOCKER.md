# Docker Deployment Guide for BHV

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### Run with Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/KathiraveluLab/BHV.git
cd BHV

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Access the application:** http://localhost:5000

### Run with Docker Only
```bash
# Build image
docker build -t bhv-app .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/bhv.db:/app/bhv.db \
  -v $(pwd)/static/uploads:/app/static/uploads \
  --name bhv \
  bhv-app

# View logs
docker logs -f bhv

# Stop
docker stop bhv
docker rm bhv
```

## Features

### Persistent Data

The Docker setup uses volumes to persist:
- **Database:** `bhv.db` is mounted from host
- **Uploads:** `static/uploads/` is mounted from host

This means your data survives container restarts!

### Health Checks

The container includes health checks:
```bash
# Check container health
docker ps

# Should show "healthy" status
```

### Automatic Restart

The container automatically restarts unless explicitly stopped:
```yaml
restart: unless-stopped
```

## Development with Docker

### Live Reload (Development Mode)

For development with live reload:
```bash
# Override the command
docker-compose run --rm -p 5000:5000 web python bhv/app.py
```

### Run Commands Inside Container
```bash
# Open shell
docker-compose exec web bash

# Run Python console
docker-compose exec web python

# Create admin user
docker-compose exec web python -c "
from bhv.app import create_app, db, User
app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print('Admin created!')
"
```

## Troubleshooting

### Port Already in Use

If port 5000 is taken, change it in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Permission Issues

On Linux/Mac, you might need to fix permissions:
```bash
sudo chown -R $USER:$USER bhv.db static/uploads
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Clean Everything
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker rmi bhv-app
```

## Production Deployment

### Environment Variables

For production, set these in `docker-compose.yml` or `.env` file:
```yaml
environment:
  - SECRET_KEY=your-super-secret-key-here
  - FLASK_ENV=production
  - DATABASE_URL=sqlite:///bhv.db
```

### Using .env File

Create `.env` file:
```
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

Then reference in `docker-compose.yml`:
```yaml
env_file:
  - .env
```

### Behind Nginx (Recommended)

For production, run behind Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### HTTPS with Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

## Performance

### Resource Limits

Add resource limits in `docker-compose.yml`:
```yaml
services:
  web:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Multi-Worker Setup

For high traffic, use Gunicorn:

Update `Dockerfile` CMD:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "bhv.app:create_app()"]
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

## Monitoring

### Container Stats
```bash
# Real-time stats
docker stats bhv-app

# Memory usage
docker stats --no-stream bhv-app
```

### Logs to File
```bash
docker-compose logs > bhv.log
```

## Backup

### Backup Database and Uploads
```bash
# Create backup directory
mkdir -p backups

# Backup database
docker cp bhv-app:/app/bhv.db backups/bhv_$(date +%Y%m%d).db

# Backup uploads
docker cp bhv-app:/app/static/uploads backups/uploads_$(date +%Y%m%d)
```

### Restore from Backup
```bash
# Stop container
docker-compose down

# Restore database
cp backups/bhv_20240101.db bhv.db

# Restore uploads
cp -r backups/uploads_20240101/* static/uploads/

# Start container
docker-compose up -d
```

## Security Best Practices

1. **Change default SECRET_KEY**
2. **Use environment variables** for sensitive data
3. **Run behind reverse proxy** (Nginx)
4. **Enable HTTPS** with Let's Encrypt
5. **Regular backups** of database and uploads
6. **Update base image** regularly
7. **Scan for vulnerabilities:** `docker scan bhv-app`

## Commands Reference
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Shell access
docker-compose exec web bash

# Python console
docker-compose exec web python

# Check health
docker ps
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify health: `docker ps`
3. Rebuild: `docker-compose up -d --build`
4. Open issue on GitHub

## License

BSD-3-Clause (same as project)