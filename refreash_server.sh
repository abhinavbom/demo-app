APP_DIR="/home/ubuntu/midfield-backend"
VENV_DIR="$APP_DIR/env"

source $VENV_DIR/bin/activate
git pull
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart gunicorn
sudo systemctl restart nginx