# 🚀 Deployment Guide

This guide provides step-by-step instructions for deploying the Room Allocation System to various platforms.

## 📋 Pre-Deployment Checklist

Before deploying, ensure:
- [ ] Application runs successfully locally
- [ ] All dependencies are listed in `requirements.txt`
- [ ] Configuration files are properly set up
- [ ] Admin password is configured (default: `trainee`)
- [ ] All features have been tested

## 🌐 Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is the easiest and most cost-effective way to deploy this application.

### Prerequisites
- GitHub account
- Repository containing the application code
- Streamlit Community Cloud account (free)

### Step-by-Step Deployment

1. **Prepare Your Repository**
   ```bash
   # Ensure your repository is up to date
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Access Streamlit Community Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Create New App**
   - Click "New app"
   - Select your repository
   - Choose the main branch
   - Set main file path: `app.py`
   - Click "Deploy!"

4. **Wait for Deployment**
   - Streamlit will install dependencies automatically
   - Initial deployment may take 2-3 minutes
   - You'll receive a unique URL for your application

5. **Verify Deployment**
   - Test all major features
   - Verify admin access works
   - Check form submissions
   - Test analytics dashboard

### Configuration for Streamlit Cloud

The application is pre-configured for Streamlit Cloud with:
- Proper port configuration (8501)
- CORS settings
- Security configurations
- Theme settings

### Custom Domain (Optional)

To use a custom domain:
1. Go to your app settings in Streamlit Cloud
2. Add your custom domain
3. Configure DNS settings as instructed
4. Enable HTTPS (automatic)

## 🐳 Docker Deployment

For containerized deployment, use Docker.

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p storage/archive

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build the image
docker build -t room-allocation-system .

# Run the container
docker run -d \
  --name room-allocation \
  -p 8501:8501 \
  -v $(pwd)/storage:/app/storage \
  room-allocation-system

# Check logs
docker logs room-allocation

# Stop the container
docker stop room-allocation
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  room-allocation:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./storage:/app/storage
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## ☁️ Cloud Platform Deployment

### Heroku

1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI (varies by OS)
   # For Ubuntu/Debian:
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Railway

1. **Connect Repository**
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Configure Build**
   - Railway auto-detects Python applications
   - Ensure `requirements.txt` is present

3. **Set Environment Variables**
   ```
   PORT=8501
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

4. **Deploy**
   - Railway automatically deploys on git push

### Google Cloud Run

1. **Create Dockerfile** (use the Docker section above)

2. **Build and Push to Container Registry**
   ```bash
   # Configure gcloud
   gcloud auth configure-docker

   # Build and tag
   docker build -t gcr.io/YOUR_PROJECT_ID/room-allocation .

   # Push to registry
   docker push gcr.io/YOUR_PROJECT_ID/room-allocation
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy room-allocation \
     --image gcr.io/YOUR_PROJECT_ID/room-allocation \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8501
   ```

## 🔧 Environment Configuration

### Environment Variables

Set these environment variables for production:

```bash
# Server Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Security (Optional)
ADMIN_PASSWORD=your_secure_password

# Performance (Optional)
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```

### Configuration Files

Ensure these files are properly configured:

1. **`.streamlit/config.toml`** - Streamlit configuration
2. **`requirements.txt`** - Python dependencies
3. **`README.md`** - Documentation

## 🔒 Production Security

### Security Checklist

- [ ] Change default admin password
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Configure proper CORS settings
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Regular security updates

### Admin Password

To change the admin password:

1. Edit `utils/security.py`
2. Update the `admin_password_hash` in `SecurityManager.__init__`
3. Use a strong password hash

```python
import hashlib
new_password = "your_secure_password"
password_hash = hashlib.sha256(new_password.encode()).hexdigest()
```

## 📊 Monitoring and Maintenance

### Health Checks

The application includes health check endpoints:
- `/_stcore/health` - Streamlit health check
- Application automatically handles errors gracefully

### Logging

Monitor application logs for:
- Failed login attempts
- Rate limiting triggers
- Data storage errors
- Performance issues

### Backup Strategy

1. **Data Backup**
   - Regularly backup the `storage/` directory
   - Archive old data periodically
   - Test restore procedures

2. **Code Backup**
   - Use version control (Git)
   - Tag releases
   - Maintain deployment documentation

### Performance Monitoring

Monitor these metrics:
- Response times
- Memory usage
- Storage space
- User activity

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Check for missing system dependencies

2. **Runtime Errors**
   - Check application logs
   - Verify file permissions
   - Ensure storage directory exists

3. **Performance Issues**
   - Monitor memory usage
   - Check for large data files
   - Optimize data processing

4. **Access Issues**
   - Verify port configuration
   - Check firewall settings
   - Confirm URL accessibility

### Debug Mode

For debugging, enable development mode:

```toml
# .streamlit/config.toml
[global]
developmentMode = true

[server]
runOnSave = true
```

## 📈 Scaling Considerations

### Horizontal Scaling

For high-traffic scenarios:
- Use load balancers
- Implement session affinity
- Consider database backend
- Cache frequently accessed data

### Vertical Scaling

For better performance:
- Increase memory allocation
- Use faster storage
- Optimize data processing
- Implement caching strategies

## 🔄 Updates and Maintenance

### Regular Updates

1. **Security Updates**
   - Update dependencies regularly
   - Monitor security advisories
   - Apply patches promptly

2. **Feature Updates**
   - Test in staging environment
   - Deploy during low-traffic periods
   - Monitor for issues post-deployment

3. **Data Maintenance**
   - Archive old data
   - Clean up temporary files
   - Optimize storage usage

### Rollback Strategy

Prepare for rollbacks:
1. Tag stable releases
2. Maintain previous version
3. Document rollback procedures
4. Test rollback process

---

**Need help with deployment? Check the main README.md or submit an issue.**

