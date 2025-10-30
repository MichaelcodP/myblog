set -e  # Exit on any error

echo "Starting MyBlog server setup..."

# Update system packages
echo "Updating system packages..."
apt update && apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
apt install -y software-properties-common build-essential curl git unzip wget tree htop nano
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
apt install -y postgresql-client redis-server nginx supervisor fail2ban ufw

# Create application user
echo "Creating application user..."
if ! id "myblog" &>/dev/null; then
    useradd -m -s /bin/bash myblog
    usermod -aG sudo myblog
    echo "User 'myblog' created"
fi

# Configure Redis
echo "Configuring Redis..."
systemctl start redis-server
systemctl enable redis-server

# Configure firewall
echo "Configuring firewall..."
ufw --force reset
ufw allow 22 80 443
ufw --force enable

# Create project directory
echo "Creating project directory..."
mkdir -p /home/myblog/myblog_project /home/myblog/logs
chown myblog:myblog /home/myblog/myblog_project /home/myblog/logs

echo "Server setup completed!"
echo "Next: Switch to myblog user and run deploy_app.sh"
