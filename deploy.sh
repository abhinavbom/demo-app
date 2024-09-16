#!/bin/bash

set -e

# Define variables
APP_DIR="/home/ubuntu/midfield-backend"
VENV_DIR="$APP_DIR/venv"
GUNICORN_SOCKET="$APP_DIR/midfield.sock"
GUNICORN_LOG="$APP_DIR/gunicorn.log"
GUNICORN_ACCESS_LOG="$APP_DIR/gunicorn-access.log"
NGINX_CONF="/etc/nginx/sites-available/midfield-backend"
GUARDRAILS_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNTM0Mzg0MzQxNTkzMTI3NDE5NCIsImFwaUtleUlkIjoiMzg4ZjljNmItODhlNC00NGNiLWE2MTgtN2EyZGNmYzg5NTAxIiwiaWF0IjoxNzIyNzg5NzI1LCJleHAiOjQ4NzYzODk3MjV9.qwHppDtqhOTRurS23e_1JYMNtD-v-Cdlx3Iv85-lEKQ"

# Create app folder if it doesn't exist
echo "Creating app folder"
sudo mkdir -p $APP_DIR

# Sync files to app folder
echo "Syncing files to app folder"
sudo rsync -av --exclude 'venv' . $APP_DIR

# Navigate to the app directory
cd $APP_DIR

# Move .env file if it exists
if [ -f env ]; then
    echo "Moving .env file"
    sudo mv env .env
else
    echo ".env file not found, skipping"
fi

# Changing ownership to the current user
echo "Changing ownership to the current user"
sudo chown -R $USER:$USER $APP_DIR

# Install Python, pip, and venv if not already installed
sudo apt-get update
echo "Installing python, pip, and venv"
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies for building some Python packages
echo "Installing system dependencies"
sudo apt-get install -y pkg-config cmake

# Install expect
echo "Installing expect"
sudo apt-get install -y expect

# Create and activate a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment"
    sudo python3 -m venv $VENV_DIR
    sudo chown -R $USER:$USER $VENV_DIR
fi

echo "Activating virtual environment"
source $VENV_DIR/bin/activate

# Install application dependencies from requirements.txt
echo "Installing application dependencies from requirements.txt"
pip install -r requirements.txt

# Configure Guardrails API key using expect
echo "Configuring Guardrails API key"
expect << EOF
spawn guardrails configure
expect "Enable anonymous metrics reporting? \[Y/n\]:"
send "n\r"
expect "Do you wish to use remote inferencing? \[Y/n\]:"
send "n\r"
expect "API Key:"
send "$GUARDRAILS_API_KEY\r"
expect eof
EOF

# Install Guardrails hub packages
echo "Installing Guardrails hub packages"
guardrails hub install hub://arize-ai/dataset_embeddings_guardrails
guardrails hub install hub://scb-10x/correct_language
guardrails hub install hub://guardrails/detect_prompt_injection
guardrails hub install hub://aryn/extractive_summary
guardrails hub install hub://guardrails/nsfw_text
guardrails hub install hub://guardrails/provenance_embeddings
guardrails hub install hub://guardrails/qa_relevance_llm_eval
guardrails hub install hub://tryolabs/restricttotopic
guardrails hub install hub://guardrails/secrets_present
guardrails hub install hub://guardrails/similar_to_previous_values
guardrails hub install hub://guardrails/wiki_provenance
guardrails hub install hub://hyparam/csv_validator
guardrails hub install hub://guardrails/ends_with
guardrails hub install hub://cartesia/financial_tone
guardrails hub install hub://guardrails/llm_critic
guardrails hub install hub://cartesia/mentions_drugs
guardrails hub install hub://guardrails/politeness_check
guardrails hub install hub://guardrails/reading_level
guardrails hub install hub://guardrails/redundant_sentences
guardrails hub install hub://guardrails/response_evaluator
guardrails hub install hub://guardrails/sensitive_topics
guardrails hub install hub://guardrails/two_words
guardrails hub install hub://guardrails/uppercase
guardrails hub install hub://guardrails/valid_choices
guardrails hub install hub://guardrails/valid_length
guardrails hub install hub://reflex/valid_python
guardrails hub install hub://guardrails/valid_sql
guardrails hub install hub://guardrails/web_sanitization
guardrails hub install hub://guardrails/valid_url
guardrails hub install hub://guardrails/valid_range
guardrails hub install hub://guardrails/valid_open_api_spec
guardrails hub install hub://guardrails/valid_json
guardrails hub install hub://guardrails/valid_address
guardrails hub install hub://guardrails/unusual_prompt
guardrails hub install hub://numbersstation/sql_column_presence
guardrails hub install hub://guardrails/responsiveness_check
guardrails hub install hub://guardrails/regex_match
guardrails hub install hub://guardrails/reading_time
guardrails hub install hub://cartesia/quotes_price
guardrails hub install hub://guardrails/one_line
guardrails hub install hub://guardrails/lowercase
guardrails hub install hub://guardrails/has_url
guardrails hub install hub://guardrails/exclude_sql_predicates
guardrails hub install hub://guardrails/endpoint_is_reachable
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/similar_to_document
guardrails hub install hub://guardrails/saliency_check
guardrails hub install hub://arize-ai/relevancy_evaluator
guardrails hub install hub://guardrails/provenance_llm
guardrails hub install hub://guardrails/profanity_free
guardrails hub install hub://guardrails/logic_check
guardrails hub install hub://guardrails/gibberish_text
guardrails hub install hub://guardrails/extracted_summary_sentences_match
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/competitor_check

# Update and install Nginx if not already installed
if ! command -v nginx > /dev/null; then
    echo "Installing Nginx"
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Configure Nginx to act as a reverse proxy if not already configured
if [ ! -f $NGINX_CONF ]; then
    echo "Configuring Nginx"
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c "cat > $NGINX_CONF <<EOF
server {
    listen 80;
    server_name api.midfield.ai;

    location / {
        include proxy_params;
        proxy_pass http://unix:$GUNICORN_SOCKET;
    }

    error_log /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
}
EOF"

    sudo ln -s $NGINX_CONF /etc/nginx/sites-enabled/
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
echo "Stopping any existing Gunicorn process"
sudo pkill gunicorn || true

# Activate the virtual environment and start Gunicorn with the Django application
echo "Starting Gunicorn"
source $VENV_DIR/bin/activate

# Export PYTHONPATH to ensure the project module is found
export PYTHONPATH=$PYTHONPATH:$APP_DIR

sudo $VENV_DIR/bin/gunicorn --workers 3 --bind unix:$GUNICORN_SOCKET midfield.wsgi:application --daemon --user www-data --group www-data --log-file $GUNICORN_LOG --access-logfile $GUNICORN_ACCESS_LOG

# Set permissions
echo "Setting permissions"
sudo chown -R www-data:www-data $APP_DIR

# Display status for debugging
echo "Checking Gunicorn status"
ps aux | grep gunicorn

echo "Checking Gunicorn log"
sudo cat $GUNICORN_LOG

echo "Checking Nginx error log"
sudo cat /var/log/nginx/error.log

echo "Deployment complete 🚀"
