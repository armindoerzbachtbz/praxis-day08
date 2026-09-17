#!/bin/bash
# deploy.sh — The TechStyle deployment script
#
# Usage: ./deploy.sh
#
# Required:
#   EC2_HOST=<public-ip-or-dns>
#
# Optional:
#   EC2_USER=ubuntu
#   KEY_PATH=~/.ssh/id_ed25519
#   REMOTE_DIR=/home/ubuntu/techstyle

set -euo pipefail

EC2_USER="${EC2_USER:-ubuntu}"
REMOTE_DIR="${REMOTE_DIR:-/home/ubuntu/techstyle}"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/id_ed25519}"

if [ -z "${EC2_HOST:-}" ]; then
  echo "ERROR: EC2_HOST is not set."
  echo "Example: EC2_HOST=1.2.3.4 ./deploy.sh"
  exit 1
fi

SERVER="${EC2_USER}@${EC2_HOST}"
SSH_OPTS=(-i "$KEY_PATH" -o StrictHostKeyChecking=accept-new)

echo "==> Deploying TechStyle to production..."
echo "    Server : $SERVER"
echo "    Path   : $REMOTE_DIR"
echo ""

echo "--> Preparing remote directory..."
ssh "${SSH_OPTS[@]}" "$SERVER" "mkdir -p '$REMOTE_DIR'"

# Step 1: Copy application files.
echo "--> Copying files..."
scp "${SSH_OPTS[@]}" -r \
  app.py \
  seed_data.py \
  requirements.txt \
  templates/ \
  static/ \
  "$SERVER:$REMOTE_DIR/"

# Step 2: Install dependencies and restart
echo "--> Installing dependencies and restarting..."
ssh "${SSH_OPTS[@]}" "$SERVER" "REMOTE_DIR='$REMOTE_DIR' bash -s" << 'ENDSSH'
  set -euo pipefail

  cd "$REMOTE_DIR"

  python3 -m venv .venv
  .venv/bin/python -m pip install --quiet --upgrade pip
  .venv/bin/python -m pip install --quiet -r requirements.txt

  .venv/bin/python - <<'PY'
import sqlite3
import seed_data

db = sqlite3.connect("/tmp/techstyle.db")
cur = db.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        image_url TEXT,
        stock INTEGER DEFAULT 100,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("SELECT COUNT(*) FROM products")
count = cur.fetchone()[0]
db.close()

if count == 0:
    seed_data.seed()
else:
    print(f"Seed skipped: products already contains {count} rows")
PY

  pkill -f "python app.py" || true
  sleep 1

  nohup .venv/bin/python app.py > techstyle.log 2>&1 &
  echo "App started with PID $!"
ENDSSH

echo ""
echo "==> Deploy complete! App running at http://$EC2_HOST:5001"
echo "    Logs: ssh -i $KEY_PATH $SERVER 'tail -f $REMOTE_DIR/techstyle.log'"
