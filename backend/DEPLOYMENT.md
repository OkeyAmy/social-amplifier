# Deployment Guide

## Production Deployment Checklist

### 1. Environment Configuration

**Update `.env` for production:**
```bash
# Use strong, randomly generated keys
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENCRYPTION_KEY=<generate-with-python-fernet-generate-key>

# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Set production CORS origins
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Disable debug mode
DEBUG=False

# Configure real OAuth credentials
LINKEDIN_CLIENT_ID=your-production-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-production-linkedin-client-secret
LINKEDIN_REDIRECT_URI=https://yourdomain.com/auth/linkedin/callback

TWITTER_CLIENT_ID=your-production-twitter-client-id
TWITTER_CLIENT_SECRET=your-production-twitter-client-secret
TWITTER_REDIRECT_URI=https://yourdomain.com/auth/twitter/callback
```

### 2. Database Setup

**Migrate to PostgreSQL:**
```bash
# Install PostgreSQL driver
pip install asyncpg

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/social_amplifier

# Initialize database
python -m app.database.init_db
```

### 3. Security Enhancements

**Generate secure keys:**
```bash
# SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (for Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Enable HTTPS:**
- Use reverse proxy (Nginx) with SSL certificates
- Configure Let's Encrypt for free SSL certificates
- Enforce HTTPS redirects

### 4. Deployment Options

#### Option A: Docker Deployment

**Create `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/social_amplifier
    depends_on:
      - db
    volumes:
      - ./.env:/app/.env

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: social_amplifier
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
```

#### Option B: Cloud Deployment (Railway, Render, Heroku)

**Railway.app:**
1. Connect GitHub repository
2. Configure environment variables in dashboard
3. Railway auto-deploys on push

**Render.com:**
1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables

**Heroku:**
```bash
# Create Procfile
echo "web: python main.py" > Procfile

# Deploy
heroku create social-amplifier-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

#### Option C: VPS Deployment (DigitalOcean, AWS EC2, Linode)

**Install dependencies:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx postgresql postgresql-contrib
```

**Setup application:**
```bash
cd /var/www
git clone your-repo social-amplifier
cd social-amplifier/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure systemd service:**
```ini
# /etc/systemd/system/social-amplifier.service
[Unit]
Description=Social Amplifier API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/social-amplifier/backend
Environment="PATH=/var/www/social-amplifier/backend/venv/bin"
ExecStart=/var/www/social-amplifier/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable social-amplifier
sudo systemctl start social-amplifier
```

**Configure Nginx:**
```nginx
# /etc/nginx/sites-available/social-amplifier
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable SSL:**
```bash
sudo ln -s /etc/nginx/sites-available/social-amplifier /etc/nginx/sites-enabled/
sudo certbot --nginx -d api.yourdomain.com
sudo systemctl restart nginx
```

### 5. Monitoring & Logging

**Setup logging:**
```python
# Add to main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

**Setup monitoring:**
- Use Sentry for error tracking
- Use DataDog or New Relic for performance monitoring
- Setup health check endpoints
- Configure uptime monitoring (UptimeRobot, Pingdom)

### 6. Rate Limiting & Caching

**Add Redis for caching:**
```bash
pip install redis aioredis
```

**Implement rate limiting:**
```python
# Add to requirements.txt
slowapi==0.1.9

# Use in routes
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### 7. Backup Strategy

**Database backups:**
```bash
# Daily backup cron job
0 2 * * * pg_dump -U user social_amplifier > /backups/db_$(date +\%Y\%m\%d).sql
```

**Environment backups:**
- Store `.env` securely (use secret management service)
- Never commit `.env` to version control
- Use tools like: AWS Secrets Manager, HashiCorp Vault, or 1Password

### 8. Performance Optimization

- Enable gzip compression
- Use CDN for static assets
- Implement database connection pooling
- Add caching layer (Redis)
- Use async workers for heavy tasks
- Enable database query optimization
- Set up load balancing for high traffic

### 9. Security Hardening

- Enable firewall (ufw, iptables)
- Limit SSH access
- Setup fail2ban
- Regular security updates
- Implement request rate limiting
- Add CORS restrictions
- Validate all inputs
- Use parameterized queries
- Enable security headers
- Regular dependency updates

### 10. Testing Before Production

```bash
# Run tests
pytest tests/

# Load testing
pip install locust
locust -f load_tests.py

# Security scanning
pip install bandit
bandit -r app/
```

## Post-Deployment

1. Monitor logs for errors
2. Check API response times
3. Verify OAuth flows work
4. Test content generation
5. Verify platform publishing
6. Setup automated backups
7. Configure alerts for downtime
8. Document API for frontend team
9. Create runbook for common issues
10. Schedule regular security audits
