set -e

DOMAIN=${1:-"_"}  # Use provided domain or default to "_" (any domain)

echo "Setting up Nginx for MyBlog..."
echo "Domain: $DOMAIN"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    echo "Usage: sudo bash setup_nginx.sh [domain]"
    exit 1
fi

# Update domain in nginx config
echo "Configuring Nginx..."
if [ "$DOMAIN" != "_" ]; then
    # Replace placeholder domain with actual domain
    sed "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" deployment/nginx.conf > /tmp/nginx-myblog.conf
else
    cp deployment/nginx.conf /tmp/nginx-myblog.conf
fi

# Install the configuration
cp /tmp/nginx-myblog.conf /etc/nginx/sites-available/myblog

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Enable MyBlog site
ln -sf /etc/nginx/sites-available/myblog /etc/nginx/sites-enabled/myblog

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Restart Nginx
echo "Restarting Nginx..."
systemctl restart nginx
systemctl enable nginx

# Create nginx rate limiting configuration
echo "Adding rate limiting to main nginx.conf..."
if ! grep -q "limit_req_zone" /etc/nginx/nginx.conf; then
    sed -i '/http {/a \    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;' /etc/nginx/nginx.conf
    nginx -t && systemctl reload nginx
fi

# Check status
echo ""
echo "Nginx Status:"
echo "================"
systemctl status nginx --no-pager -l

echo ""
echo " Nginx setup completed!"
echo ""
echo "Configuration details:"
echo "   Config file: /etc/nginx/sites-available/myblog"
echo "   Document root: /home/myblog/myblog_project/"
echo "   Domain: $DOMAIN"
echo ""
echo "Useful commands:"
echo "   nginx -t                    # Test configuration"
echo "   systemctl reload nginx      # Reload config without downtime"
echo "   systemctl restart nginx     # Full restart"
echo "   tail -f /var/log/nginx/error.log  # View error logs"
echo ""
if [ "$DOMAIN" != "_" ]; then
    echo "Next step: Set up SSL certificate:"
    echo "   sudo apt install certbot python3-certbot-nginx -y"
    echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi
