#!/bin/bash
# deploy.sh — The TechStyle deployment script
#
# Usage: ./deploy.sh
#
# This script copies the entire project to the production server via SCP,
# then SSHes in and restarts the app by killing the old process and
# starting a new one. No downtime handling. No rollback. Ship it.
#
# TODO someday: Docker, CI/CD, zero-downtime deploys... (Day 07 topic)

SERVER="ubuntu@54.93.12.108"
REMOTE_DIR="/home/ubuntu/techstyle"
KEY="~/.ssh/techstyle_prod.pem"

echo "==> Deploying TechStyle to production..."
echo "    Server : $SERVER"
echo "    Path   : $REMOTE_DIR"
echo ""

# Step 1: Copy everything over (including __pycache__, .env, everything)
echo "--> Copying files..."
scp -i "$KEY" -r \
  app.py \
  seed_data.py \
  requirements.txt \
  templates/ \
  static/ \
  "$SERVER:$REMOTE_DIR/"

if [ $? -ne 0 ]; then
  echo "ERROR: SCP failed. Check your SSH key and server IP."
  exit 1
fi

# Step 2: Install dependencies and restart
echo "--> Installing dependencies and restarting..."
ssh -i "$KEY" "$SERVER" << 'ENDSSH'
  cd /home/ubuntu/techstyle
  pip install -r requirements.txt --quiet
  # Kill the old app (gracefully... or not)
  pkill -f "python app.py" || true
  sleep 1
  # Start in background, log to file
  nohup python app.py > /var/log/techstyle.log 2>&1 &
  echo "App started with PID $!"
ENDSSH

echo ""
echo "==> Deploy complete! App running at http://$SERVER:5000"
echo "    Logs: ssh -i $KEY $SERVER 'tail -f /var/log/techstyle.log'"
