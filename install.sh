#!/bin/bash
# FreeNode One-liner Installer
# Usage: curl -s https://raw.githubusercontent.com/macmam1/freenode/main/install.sh | bash
# Or: bash -c "$(curl -fsSL https://deploy.freenode.dev/install.sh)" -- --platform render

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}FreeNode Installation Script${NC}"
echo "========================================"

# Parse arguments
PLATFORM="${1:-auto}"
API_TOKEN="${2:-}"
DASHBOARD_PORT="${3:-8080}"

# Detect platform if auto
if [ "$PLATFORM" = "auto" ]; then
    if [ -n "$RENDER" ]; then
        PLATFORM="render"
    elif [ -n "$RAILWAY_ENVIRONMENT" ]; then
        PLATFORM="railway"
    elif [ -n "$FLY_APP_NAME" ]; then
        PLATFORM="fly"
    elif [ -n "$KAGGLE_DATA_SECRETS_PATH" ]; then
        PLATFORM="kaggle"
    elif [ -n "$COLAB_GPU" ]; then
        PLATFORM="colab"
    else
        PLATFORM="generic"
    fi
fi

echo -e "${YELLOW}Platform detected: $PLATFORM${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if command -v apt-get &> /dev/null; then
    apt-get update -qq
    apt-get install -y -qq python3-pip git curl wget &>/dev/null
elif command -v yum &> /dev/null; then
    yum install -y -q python3-pip git curl wget &>/dev/null
elif command -v brew &> /dev/null; then
    brew install -q python3 git curl wget &>/dev/null
fi

# Clone or update FreeNode
FREENODE_DIR="${HOME}/.freenode"
if [ -d "$FREENODE_DIR" ]; then
    echo -e "${YELLOW}Updating existing FreeNode installation...${NC}"
    cd "$FREENODE_DIR"
    git pull -q origin main
else
    echo -e "${YELLOW}Cloning FreeNode repository...${NC}"
    git clone -q https://github.com/macmam1/freenode.git "$FREENODE_DIR"
    cd "$FREENODE_DIR"
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
python3 -m pip install -q -r requirements.txt 2>/dev/null || python3 -m pip install -q fastapi uvicorn psutil pydantic

# Create configuration
echo -e "${YELLOW}Creating configuration...${NC}"
cat > "$FREENODE_DIR/freenode.yaml" << EOF
platform: "$PLATFORM"
dashboard_port: $DASHBOARD_PORT
api_token: "$API_TOKEN"
modules:
  ssh: "disabled"
  tunnel: "disabled"
  keepalive: "enabled"
  api: "enabled"
  terminal: "enabled"
deception:
  log_scrub: true
  behavioral_mimicry: true
  string_encryption: true
obfuscation:
  quiet_mode: false
  artifact_strip: true
  anti_analysis: true
EOF

# Create systemd service (if root)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Setting up systemd service...${NC}"
    cat > /etc/systemd/system/freenode.service << EOF
[Unit]
Description=FreeNode Service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
WorkingDirectory=$FREENODE_DIR
ExecStart=/usr/bin/python3 -m src.dashboard.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable freenode
    systemctl start freenode
    echo -e "${GREEN}✓ Service installed and started${NC}"
else
    echo -e "${YELLOW}Not running as root, creating startup script instead...${NC}"
    cat > "$FREENODE_DIR/start.sh" << 'SCRIPT'
#!/bin/bash
cd $(dirname "$0")
python3 -m src.dashboard.app
SCRIPT
    chmod +x "$FREENODE_DIR/start.sh"
fi

# Create keepalive loop
echo -e "${YELLOW}Setting up keepalive mechanism...${NC}"
cat > "$FREENODE_DIR/keepalive.sh" << 'KEEPALIVE'
#!/bin/bash
FREENODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH_URL="http://localhost:8080/api/status"
INTERVAL=180

while true; do
    if ! pgrep -f "src.dashboard.app" > /dev/null; then
        echo "[$(date)] FreeNode process died, restarting..."
        cd "$FREENODE_DIR"
        python3 -m src.dashboard.app &
        sleep 5
    fi
    
    # Health check ping
    curl -s "$HEALTH_URL" > /dev/null 2>&1 || true
    
    sleep $INTERVAL
done
KEEPALIVE
chmod +x "$FREENODE_DIR/keepalive.sh"

# Start dashboard in background
echo -e "${YELLOW}Starting FreeNode Dashboard...${NC}"
cd "$FREENODE_DIR"
nohup python3 -m src.dashboard.app > /tmp/freenode.log 2>&1 &
DASHBOARD_PID=$!
sleep 2

# Verify installation
if curl -s http://localhost:$DASHBOARD_PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
    echo ""
    echo -e "${GREEN}Dashboard URL:${NC} http://localhost:$DASHBOARD_PORT"
    echo -e "${GREEN}PID:${NC} $DASHBOARD_PID"
    echo -e "${GREEN}Config:${NC} $FREENODE_DIR/freenode.yaml"
    echo -e "${GREEN}Logs:${NC} /tmp/freenode.log"
    echo ""
    echo "Platform: $PLATFORM"
    echo "Region: $(curl -s https://api.ipify.org)"
else
    echo -e "${RED}✗ Installation failed. Check logs: /tmp/freenode.log${NC}"
    tail -20 /tmp/freenode.log
    exit 1
fi

# Setup auto-restart cron job
(crontab -l 2>/dev/null || true; echo "*/5 * * * * $FREENODE_DIR/keepalive.sh > /tmp/freenode-keepalive.log 2>&1") | crontab - 2>/dev/null || true

echo -e "${GREEN}Installation complete!${NC}"
