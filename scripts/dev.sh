#!/usr/bin/env bash
# ==============================================================================
# ScamGuard Unified Development Server Runner
# Starts FastAPI backend (port 8000) and React Vite frontend (port 5173)
# ==============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}====================================================${NC}"
echo -e "${RED}           🛡️  ScamGuard Dev Server Launch          ${NC}"
echo -e "${RED}====================================================${NC}"

# Check backend venv
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}Warning: Python virtual environment not found in backend/venv.${NC}"
    echo "Creating virtualenv..."
    python3 -m venv "$BACKEND_DIR/venv"
    "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

# Check frontend node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}Warning: node_modules not found in frontend/.${NC}"
    echo "Running npm install..."
    cd "$FRONTEND_DIR" && npm install
fi

# Cleanup trap to kill child processes on Ctrl+C
cleanup() {
    echo -e "\n${YELLOW}Shutting down ScamGuard servers...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}Servers stopped cleanly.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo -e "${BLUE}Starting FastAPI Backend on http://localhost:8000...${NC}"
cd "$BACKEND_DIR"
PYTHONPATH=. "$BACKEND_DIR/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo -e "${BLUE}Starting Vite Frontend on http://localhost:5173...${NC}"
cd "$FRONTEND_DIR"
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✓ ScamGuard is running!${NC}"
echo -e "  • Web Interface:      ${GREEN}http://localhost:5173${NC}"
echo -e "  • API & Health:       ${GREEN}http://localhost:8000/health${NC}"
echo -e "  • WebSocket Stream:   ${GREEN}ws://localhost:8000/ws/call${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to terminate all servers.${NC}"

# Wait indefinitely for processes
wait
