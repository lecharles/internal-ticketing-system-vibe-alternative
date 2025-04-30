#!/bin/bash

# Exit on error
set -e

echo "Deploying to test environment..."

# 1. Set environment variables
export FLASK_ENV=testing
export FLASK_APP=app
export DATABASE_URL="postgresql://localhost/internal_jira_test"

# 2. Update code
git pull origin main

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run database migrations
flask db upgrade

# 5. Create SSL directory if it doesn't exist
sudo mkdir -p /etc/nginx/ssl

# 6. Generate self-signed SSL certificate for testing
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/internal-jira.key \
    -out /etc/nginx/ssl/internal-jira.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=internal-jira.example.com"

# 7. Copy Nginx configuration
sudo cp config/nginx/nginx.conf /etc/nginx/sites-available/internal-jira
sudo ln -sf /etc/nginx/sites-available/internal-jira /etc/nginx/sites-enabled/

# 8. Create logs directory
mkdir -p logs

# 9. Set proper permissions
sudo chown -R www-data:www-data logs/
sudo chmod -R 755 logs/

# 10. Restart services
sudo systemctl restart nginx
sudo systemctl restart gunicorn

echo "Deployment completed successfully!" 