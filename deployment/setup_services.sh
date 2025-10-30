set -e

echo "Setting up MyBlog systemd services..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    echo "Usage: sudo bash setup_services.sh"
    exit 1
fi

SERVICE_DIR="/etc/systemd/system"
PROJECT_DIR="/home/myblog/myblog_project"

# Copy service files
echo "Installing service files..."
cp deployment/myblog.service $SERVICE_DIR/
cp deployment/myblog-celery.service $SERVICE_DIR/

# Set proper permissions
chmod 644 $SERVICE_DIR/myblog.service
chmod 644 $SERVICE_DIR/myblog-celery.service

# Create socket directory
echo "Creating socket directory..."
mkdir -p /run/myblog
chown myblog:myblog /run/myblog

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable services (start on boot)
echo "Enabling services..."
systemctl enable myblog.service
systemctl enable myblog-celery.service

# Start services
echo "Starting services..."
systemctl start myblog.service
systemctl start myblog-celery.service

# Check status
echo ""
echo "Service Status:"
echo "=================="
systemctl status myblog.service --no-pager -l
echo ""
systemctl status myblog-celery.service --no-pager -l

echo ""
echo "Services setup completed!"
echo ""
echo "Useful commands:"
echo "   systemctl status myblog          # Check Django app status"
echo "   systemctl status myblog-celery   # Check Celery worker status"
echo "   systemctl restart myblog         # Restart Django app"
echo "   systemctl restart myblog-celery  # Restart Celery worker"
echo "   journalctl -u myblog -f          # View Django app logs"
echo "   journalctl -u myblog-celery -f   # View Celery logs"
