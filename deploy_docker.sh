#!/bin/bash
# deploy_docker.sh - Deploy TechStyle to EC2 with Docker Compose.
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
  echo "Example: EC2_HOST=1.2.3.4 ./deploy_docker.sh"
  exit 1
fi

SERVER="${EC2_USER}@${EC2_HOST}"
SSH_OPTS=(-i "$KEY_PATH" -o StrictHostKeyChecking=accept-new)

echo "==> Deploying TechStyle Docker version..."
echo "    Server : $SERVER"
echo "    Path   : $REMOTE_DIR"
echo ""

echo "--> Preparing remote directories..."
ssh "${SSH_OPTS[@]}" "$SERVER" "mkdir -p '$REMOTE_DIR' /opt/techstyle/data && sudo chown -R '$EC2_USER':'$EC2_USER' /opt/techstyle"

echo "--> Copying Docker deployment files..."
scp "${SSH_OPTS[@]}" -r \
  app.py \
  seed_data.py \
  requirements.txt \
  Dockerfile \
  docker-compose.yml \
  templates/ \
  static/ \
  "$SERVER:$REMOTE_DIR/"

echo "--> Building and starting Docker Compose..."
ssh "${SSH_OPTS[@]}" "$SERVER" "REMOTE_DIR='$REMOTE_DIR' bash -s" << 'ENDSSH'
  set -euo pipefail

  cd "$REMOTE_DIR"

  docker compose up -d --build

  echo "--> Waiting for container to become ready..."
  for i in $(seq 1 12); do
    if curl -fsS http://localhost:5001/api/products >/dev/null; then
      break
    fi
    echo "Waiting for app ($i/12)..."
    sleep 5
  done

  echo "--> Seeding database if needed..."
  docker compose exec -T web python - <<'PY'
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

  docker compose ps
ENDSSH

echo ""
echo "==> Docker deploy complete! App running at http://$EC2_HOST:5001"
echo "    Logs: ssh -i $KEY_PATH $SERVER 'cd $REMOTE_DIR && docker compose logs -f web'"
