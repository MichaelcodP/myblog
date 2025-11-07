set -e

APP_DIR="/home/myblog/myblog_project"
BRANCH="main"

echo "Updating MyBlog application..."

# Check if running as myblog user
if [ "$USER" != "myblog" ]; then
    echo "This script must be run as the 'myblog' user"
    exit 1
fi

cd $APP_DIR

# Pull latest code
echo "Pulling latest code..."
git fetch origin
git reset --hard origin/$BRANCH

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Updating dependencies..."
pip install -r requirements.txt

# Run Django updates
echo "Running Django updates..."
python manage.py collectstatic --noinput
python manage.py migrate

# Restart application (will be configured later with systemd)
echo "Restarting application..."
sudo systemctl restart myblog || echo "Service not configured yet"
sudo systemctl restart nginx || echo "Nginx not configured yet"

echo "Update completed!"
