# MyBlog Deployment Quick Reference

## íº€ Initial Deployment Commands

```bash
# 1. Setup server (run once)
sudo bash deployment/setup_server.sh

# 2. Deploy application (as myblog user)
sudo su - myblog
bash deployment/deploy_app.sh

# 3. Configure services (as root)
exit
sudo bash deployment/setup_services.sh

# 4. Setup web server (as root)
sudo bash deployment/setup_nginx.sh your-domain.com
```

## í´„ Update Application

```bash
# Quick update (as myblog user)
sudo su - myblog
bash deployment/update_app.sh
```

## í³Š Monitoring Commands

```bash
# Check service status
sudo systemctl status myblog
sudo systemctl status myblog-celery  
sudo systemctl status nginx

# View logs in real-time
journalctl -u myblog -f
journalctl -u myblog-celery -f
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart myblog
sudo systemctl restart myblog-celery
sudo systemctl restart nginx
```

## í°› Troubleshooting

```bash
# Test Django app manually
sudo su - myblog
cd /home/myblog/myblog_project
source venv/bin/activate
python manage.py check

# Test Nginx configuration
sudo nginx -t

# Fix permissions
sudo chown -R myblog:myblog /home/myblog/myblog_project
```
