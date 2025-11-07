set -e  # Exit on any error

APP_DIR="/home/myblog/myblog_project"
REPO_URL="https://github.com/MichaelcodP/myblog.git"
BRANCH="main"  # Change to your main branch

echo "Starting MyBlog application deployment..."

# Check if we're running as myblog user
if [ "$USER" != "myblog" ]; then
    echo "This script must be run as the 'myblog' user"
    echo "Run: sudo su - myblog"
    exit 1
fi

# 1. CLONE OR UPDATE CODE

if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR
    git fetch origin
    git reset --hard origin/$BRANCH
else
    echo "Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
    git checkout $BRANCH
fi

echo "Code updated!"

# 2. SETUP PYTHON VIRTUAL ENVIRONMENT

echo "Setting up Python virtual environment..."

if [ ! -d "$APP_DIR/venv" ]; then
    python3.11 -m venv $APP_DIR/venv
    echo "Virtual environment created"
fi

# Activate virtual environment
source $APP_DIR/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

echo "Virtual environment ready!"

# 3. INSTALL PYTHON DEPENDENCIES
echo "Installing Python dependencies..."

pip install -r requirements.txt

echo "Dependencies installed!"

# 4. SETUP ENVIRONMENT FILE
echo "Setting up environment file..."

if [ ! -f "$APP_DIR/.env" ]; then
    echo ".env file not found!"
    echo "Please create .env file with your production settings"
    echo "You can use .env.production.template as a reference"
    echo ""
    echo "Required variables:"
    echo "- DEBUG=False"
    echo "- SECRET_KEY=your-secret-key"
    echo "- ALLOWED_HOSTS=your-domain,your-ip"
    echo "- Database settings (DB_NAME, DB_USER, etc.)"
    echo "- AWS S3 settings"
    echo "- Stripe settings"
    echo ""
    echo "Deployment stopped. Create .env file first."
    exit 1
fi

echo "Environment file found!"

# 5. RUN DJANGO SETUP COMMANDS

echo "Running Django setup commands..."

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell < create_superuser.py || echo "Superuser might already exist"

echo "Django setup completed!"

# 6. TEST APPLICATION

echo "Testing application..."

# Test if Django can start
python manage.py check

echo "Application tests passed!"

# DEPLOYMENT SUMMARY

echo ""
echo "Deployment completed successfully!"
echo ""
echo "Application location: $APP_DIR"
echo "Virtual environment: $APP_DIR/venv"
echo ""
echo "Next steps:"
echo "   1. Configure systemd service (run setup systemd script)"
echo "   2. Configure nginx (run setup nginx script)"
echo "   3. Start the application service"
echo ""
echo "To manually start the app for testing:"
echo "   cd $APP_DIR"
echo "   source venv/bin/activate"
echo "   gunicorn myblog.wsgi:application --bind 0.0.0.0:8000"
EOF