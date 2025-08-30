#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while true; do
        # Try lsof first, then netstat as fallback
        if command -v lsof &> /dev/null; then
            if ! lsof -i :$port &>/dev/null; then
                break
            fi
        elif command -v netstat &> /dev/null; then
            if ! netstat -an | grep -q ":$port "; then
                break
            fi
        else
            # If neither command is available, just try the port
            if ! nc -z 127.0.0.1 $port 2>/dev/null; then
                break
            fi
        fi
        ((port++))
    done
    
    echo $port
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup on exit
cleanup() {
    print_warning "Shutting down servers..."
    # Kill all child processes
    pkill -P $
    # Clean up temporary files
    rm -f /tmp/frontend_output.log
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup INT TERM

# Main execution
print_status "Starting full-stack development environment..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -f "backend/manage.py" ]; then
    print_error "Backend directory or manage.py not found. Please run this script from your project root directory (where backend/ and frontend/ directories exist)."
    exit 1
fi

if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found. Please make sure you have a 'frontend' directory."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install Node.js and npm first."
    print_status "You can install it from: https://nodejs.org/"
    exit 1
fi

# Check if lsof is available for port checking
if ! command -v lsof &> /dev/null; then
    print_warning "lsof not found. Port conflict detection may not work properly."
    print_status "On macOS: brew install lsof"
    print_status "On Ubuntu/Debian: sudo apt-get install lsof"
fi

# Find available port for Django backend
BACKEND_PORT=$(find_available_port 8080)
if [ "$BACKEND_PORT" != "8080" ]; then
    print_warning "Port 8080 is in use, Django will use port $BACKEND_PORT instead"
fi

# Start Django backend
print_status "Setting up and starting Django backend..."
{
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment and run server
    source .venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found in backend directory"
    fi
    
    # Run Django server on available port
    print_success "Starting Django server on http://127.0.0.1:$BACKEND_PORT"
    python manage.py runserver 127.0.0.1:$BACKEND_PORT
} &

# Start npm frontend
print_status "Setting up and starting frontend..."
{
    cd frontend
    
    # Install npm packages
    print_status "Installing npm dependencies..."
    npm install
    
    # Run development server and capture output to extract URL
    print_success "Starting frontend development server..."
    
    # Start npm in background and capture its output
    npm run dev > /tmp/frontend_output.log 2>&1 &
    NPM_PID=$!
    
    # Monitor output for URL and open Chrome
    print_status "Waiting for frontend server to start..."
    FRONTEND_URL=""
    
    # Monitor the log file for URL patterns
    for i in {1..15}; do
        if [ -f "/tmp/frontend_output.log" ]; then
            # Common patterns for different frameworks
            FRONTEND_URL=$(grep -E "(Local|localhost).*http" /tmp/frontend_output.log | grep -o "http://[^[:space:]]*" | head -1)
            
            if [ -z "$FRONTEND_URL" ]; then
                FRONTEND_URL=$(grep -o "http://localhost:[0-9]*" /tmp/frontend_output.log | head -1)
            fi
            
            if [ -z "$FRONTEND_URL" ]; then
                FRONTEND_URL=$(grep -o "http://127.0.0.1:[0-9]*" /tmp/frontend_output.log | head -1)
            fi
            
            # Check for Next.js style output
            if [ -z "$FRONTEND_URL" ]; then
                FRONTEND_URL=$(grep -A2 "ready" /tmp/frontend_output.log | grep -o "http://[^[:space:]]*" | head -1)
            fi
            
            if [ -n "$FRONTEND_URL" ]; then
                print_success "Frontend server ready at: $FRONTEND_URL"
                print_status "Opening in Chrome..."
                
                # Open in Chrome (macOS)
                if command -v open &> /dev/null; then
                    open -a "Google Chrome" "$FRONTEND_URL" 2>/dev/null || \
                    open -a "Chrome" "$FRONTEND_URL" 2>/dev/null || \
                    open "$FRONTEND_URL"
                # Linux
                elif command -v google-chrome &> /dev/null; then
                    google-chrome "$FRONTEND_URL" &
                elif command -v chromium-browser &> /dev/null; then
                    chromium-browser "$FRONTEND_URL" &
                elif command -v xdg-open &> /dev/null; then
                    xdg-open "$FRONTEND_URL"
                # Windows
                elif command -v start &> /dev/null; then
                    start chrome "$FRONTEND_URL" || start "$FRONTEND_URL"
                fi
                break
            fi
        fi
        sleep 1
    done
    
    if [ -z "$FRONTEND_URL" ]; then
        print_warning "Could not auto-detect frontend URL. Check output below for the server address."
    fi
    
    # Continue showing npm output
    tail -f /tmp/frontend_output.log
} &

# Display information
sleep 2
print_success "Both servers are starting up!"
print_status "Backend: http://127.0.0.1:$BACKEND_PORT (auto-selected available port)"
print_status "Frontend: Detecting URL and opening in Chrome... (npm dev servers auto-handle port conflicts)"
print_warning "Press Ctrl+C to stop both servers"

# Wait for all background processes
wait