#!/bin/bash

# Speech-to-Text Service Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Installing Speech-to-Text Service...${NC}"

# Get current directory and user
SERVICE_DIR=$(pwd)
SERVICE_USER=$(whoami)

echo -e "${YELLOW}📁 Service directory: ${SERVICE_DIR}${NC}"
echo -e "${YELLOW}👤 Service user: ${SERVICE_USER}${NC}"

# Create service file with correct paths
SERVICE_FILE="/etc/systemd/system/speech-to-text.service"

echo -e "${GREEN}📝 Creating systemd service file...${NC}"

sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Speech-to-Text Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$SERVICE_DIR
Environment=PATH=$SERVICE_DIR/.venv/bin
ExecStart=$SERVICE_DIR/.venv/bin/python start_service.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=speech-to-text

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$SERVICE_DIR/uploads $SERVICE_DIR/output $SERVICE_DIR/audio_input

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
sudo chmod 644 $SERVICE_FILE

# Reload systemd
echo -e "${GREEN}🔄 Reloading systemd...${NC}"
sudo systemctl daemon-reload

# Enable service
echo -e "${GREEN}✅ Enabling service...${NC}"
sudo systemctl enable speech-to-text.service

# Start service
echo -e "${GREEN}🚀 Starting service...${NC}"
sudo systemctl start speech-to-text.service

# Check status
sleep 2
echo -e "${GREEN}📊 Service status:${NC}"
sudo systemctl status speech-to-text.service --no-pager

echo -e "${GREEN}✅ Installation complete!${NC}"
echo -e "${YELLOW}Commands to manage the service:${NC}"
echo -e "  ${GREEN}sudo systemctl start speech-to-text${NC}    - Start service"
echo -e "  ${GREEN}sudo systemctl stop speech-to-text${NC}     - Stop service"
echo -e "  ${GREEN}sudo systemctl restart speech-to-text${NC}  - Restart service"
echo -e "  ${GREEN}sudo systemctl status speech-to-text${NC}   - Check status"
echo -e "  ${GREEN}sudo journalctl -u speech-to-text -f${NC}   - View logs"
echo -e "  ${GREEN}curl http://localhost:8338/health${NC}      - Test service"
