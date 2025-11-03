# MyBlog AWS Deployment Guide

Complete step-by-step guide to deploy MyBlog Django application on AWS.

## ��� Prerequisites

- AWS Account (free tier eligible)
- Domain name (optional, but recommended)
- Basic terminal/SSH knowledge
- GitHub account with your code

## ��� Deployment Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Code     │    │   AWS Services  │    │   Production    │
│   (GitHub)      │───▶│   - EC2         │───▶│   - Your Blog   │
│                 │    │   - RDS         │    │   - HTTPS       │
│                 │    │   - S3          │    │   - Auto-scale  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ���️ Architecture

- **EC2**: Ubuntu server running your Django app
- **RDS**: PostgreSQL database (managed by AWS)  
- **S3**: Static files and media storage
- **Nginx**: Web server and reverse proxy
- **Gunicorn**: Python WSGI server
- **SystemD**: Process management and auto-restart

---

# ��� PART 1: AWS Infrastructure Setup

## Step 1.1: Create AWS Account (+)

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create AWS Account" 
3. Complete registration (requires credit card, but free tier available)
4. Verify email and phone number

## Step 1.2: Create S3 Bucket for Static Files (+)

1. **Go to S3 Console**: Services → S3 
2. **Create bucket**:
   - Name: `myblog-static-prod-2025` (must be globally unique)
   - Region: `us-east-1` (or your preferred region)
   - **Block all public access**: ❌ UNCHECK (we need public access for static files)
   - Create bucket

3. **Configure bucket policy**:
   - Go to bucket → Permissions → Bucket Policy
   - Add this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",  
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

## Step 1.3: Create IAM User for S3 Access (+)

1. **Go to IAM Console**: Services → IAM
2. **Create user**:
   - Username: `myblog-s3-user`
   - Access type: ✅ Programmatic access
   
3. **Attach policies**:
   - Click "Attach existing policies directly"
   - Search and select: `AmazonS3FullAccess`
   
4. **Save credentials**:
   - ⚠️ **IMPORTANT**: Save the Access Key ID and Secret Access Key
   - You'll need these for your `.env` file

## Step 1.4: Create RDS PostgreSQL Database (+)

1. **Go to RDS Console**: Services → RDS
2. **Create database**:
   - Engine: PostgreSQL
   - Template: Free tier
   - **Settings**:
     - DB instance identifier: `myblog-prod-db`
     - Master username: `myblog_admin`
     - Master password: Generate strong password (save it!)
   - **Instance configuration**:
     - DB instance class: `db.t3.micro` (free tier)
   - **Storage**: 20 GB (free tier)
   - **Connectivity**:
     - Public access: ✅ Yes (we'll secure it later)
   - Create database

3. **Note the endpoint**: You'll need this for your `.env` file
   - Example: `myblog-prod-db.ch6xo9fj3xne.us-east-1.rds.amazonaws.com`

## Step 1.5: Create EC2 Instance (+)

1. **Go to EC2 Console**: Services → EC2
2. **Launch instance**:
   - Name: `MyBlog-Production`
   - **Application and OS Images**: Ubuntu Server 22.04 LTS (free tier eligible)
   - **Instance type**: `t2.micro` (free tier)
   - **Key pair**: Create new key pair
     - Name: `myblog-key`
     - Type: RSA, .pem format
     - ⚠️ **Download and save the .pem file securely**
   
   - **Network settings**:
     - ✅ Allow SSH traffic from anywhere
     - ✅ Allow HTTP traffic from the internet  
     - ✅ Allow HTTPS traffic from the internet
   
   - **Storage**: 8 GB (free tier)
   - Launch instance

3. **Note the Public IP**: You'll need this to connect via SSH (54.87.22.77)

---

# ���️ PART 2: Server Setup and Deployment

## Step 2.1: Connect to Your EC2 Instance (+)

### On Windows (using Command Prompt or PowerShell):
```bash
# Navigate to where you saved the .pem file
cd C:\path\to\your\key

# Set proper permissions (may need Git Bash on Windows)
chmod 400 myblog-key.pem

# Connect to your server (replace YOUR-EC2-IP)
ssh -i myblog-key.pem ubuntu@YOUR-EC2-IP
```

### On Mac/Linux:
```bash
chmod 400 myblog-key.pem
ssh -i myblog-key.pem ubuntu@YOUR-EC2-IP
```

## Step 2.2: Initial Server Setup

Once connected to your EC2 instance:

```bash
# Update system (+)
sudo apt update && sudo apt upgrade -y 

# Clone your repository (+)
git clone https://github.com/MichaelcodP/myblog.git /home/ubuntu/myblog_project
cd /home/ubuntu/myblog_project

# Run server setup script (+) !!!!!
sudo bash deployment/setup_server.sh
```

## Step 2.3: Configure Environment Variables

```bash
# Switch to myblog user
sudo su - myblog

# Navigate to project
cd /home/myblog/myblog_project

# Create production environment file
cp .env.production.template .env

# Edit the environment file
nano .env
```

**Fill in your actual values**:
```bash
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

# Database (from your RDS instance)
DB_NAME=myblog_production  
DB_USER=myblog_admin
DB_PASSWORD=your-rds-password
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432

# AWS S3 (from your IAM user)
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
USE_S3=True

# Email (use Gmail for testing)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com

# Stripe (use test keys first)
STRIPE_SECRET_KEY=sk_test_your-test-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-test-key  
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

## Step 2.4: Deploy the Application

```bash
# Still as myblog user
bash deployment/deploy_app.sh
```

This script will:
- Set up Python virtual environment
- Install dependencies
- Run database migrations
- Collect static files
- Create superuser

## Step 2.5: Configure Services

```bash
# Exit back to ubuntu user  
exit

# Set up SystemD services
sudo bash deployment/setup_services.sh

# Set up Nginx
sudo bash deployment/setup_nginx.sh your-domain.com
# Or without domain: sudo bash deployment/setup_nginx.sh
```

## Step 2.6: Test Your Deployment

```bash
# Check if services are running
sudo systemctl status myblog
sudo systemctl status myblog-celery  
sudo systemctl status nginx

# Test the application
curl http://your-ec2-ip
curl http://your-ec2-ip/health/
```

---

# ��� PART 3: Security and SSL Setup

## Step 3.1: Set Up SSL Certificate (Optional but Recommended)

If you have a domain name:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 3.2: Configure Firewall

```bash
# Check firewall status
sudo ufw status

# The setup script should have already configured:
# - Port 22 (SSH)
# - Port 80 (HTTP)  
# - Port 443 (HTTPS)
```

## Step 3.3: Secure RDS Database

1. **Go to RDS Console**
2. **Modify your database**:
   - **Connectivity**: Change public access to "No"
   - **Security groups**: Create new security group that only allows access from your EC2 instance

---

# ��� PART 4: Maintenance and Updates

## Updating Your Application

```bash
# SSH to your server
ssh -i myblog-key.pem ubuntu@your-ec2-ip

# Switch to myblog user
sudo su - myblog

# Run update script
bash deployment/update_app.sh
```

## Monitoring

```bash
# Check application logs
journalctl -u myblog -f

# Check Celery logs  
journalctl -u myblog-celery -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check system resources
htop
df -h  # Disk usage
free -h  # Memory usage
```

## Backup Database

```bash
# Create database backup
pg_dump -h your-rds-endpoint.rds.amazonaws.com \
        -U myblog_admin \
        -d myblog_production > backup.sql

# Restore from backup
psql -h your-rds-endpoint.rds.amazonaws.com \
     -U myblog_admin \
     -d myblog_production < backup.sql
```

---

# ��� Troubleshooting

## Common Issues

### 1. "502 Bad Gateway" Error
```bash
# Check if Django app is running
sudo systemctl status myblog

# Check socket file exists
ls -la /home/myblog/myblog_project/myblog.sock

# Restart services
sudo systemctl restart myblog
sudo systemctl restart nginx
```

### 2. Static Files Not Loading
```bash
# Check S3 configuration in .env
cat /home/myblog/myblog_project/.env | grep AWS

# Re-collect static files
sudo su - myblog
cd /home/myblog/myblog_project
source venv/bin/activate
python manage.py collectstatic --clear
```

### 3. Database Connection Issues
```bash
# Test database connection
sudo su - myblog
cd /home/myblog/myblog_project  
source venv/bin/activate
python manage.py dbshell
```

### 4. Permission Issues
```bash
# Fix file permissions
sudo chown -R myblog:myblog /home/myblog/myblog_project
sudo chmod -R 755 /home/myblog/myblog_project
```

---

# ��� Performance Optimization

## Enable Redis Caching
```bash
# Redis is already installed, configure in Django settings
# Add to .env:
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Monitor Resources
```bash
# Set up basic monitoring
sudo apt install htop iotop nethogs -y

# Check what's using resources
htop      # CPU and memory
iotop     # Disk I/O  
nethogs   # Network usage
```

---

# ✅ Deployment Checklist

- [ ] AWS account created
- [ ] S3 bucket created and configured
- [ ] IAM user created with S3 access
- [ ] RDS PostgreSQL database created
- [ ] EC2 instance launched
- [ ] SSH key pair downloaded and secured
- [ ] Connected to EC2 instance via SSH
- [ ] Server setup script executed
- [ ] Environment variables configured
- [ ] Application deployed successfully
- [ ] SystemD services configured and running
- [ ] Nginx configured and running
- [ ] Application accessible via browser
- [ ] SSL certificate configured (if domain available)
- [ ] Firewall properly configured
- [ ] Database secured
- [ ] Monitoring set up
- [ ] Backup strategy implemented

---

# ��� Success!

Your MyBlog application should now be:
- ✅ Running on AWS EC2
- ✅ Using managed PostgreSQL database
- ✅ Storing files on S3
- ✅ Serving HTTPS traffic (if SSL configured)
- ✅ Auto-restarting if it crashes
- ✅ Ready for production use

## Next Steps

1. **Domain Configuration**: Point your domain to your EC2 IP
2. **Monitoring**: Set up CloudWatch or similar monitoring
3. **Backup**: Implement automated database and file backups
4. **Scaling**: Consider load balancers and auto-scaling groups
5. **CI/CD**: Set up automated deployment pipelines

---

*This guide was created for MyBlog Django application deployment on AWS. For support, check the troubleshooting section or create an issue in the GitHub repository.*
