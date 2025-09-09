#!/bin/bash

# generate_keys.sh - Generate secure API keys and JWT secrets
# Run this script to generate cryptographically secure keys for your BrainDrive Document AI
# Compatible with macOS and Linux

set -e  # Exit on any error

# Default values
LENGTH=64
ENV_FILE=".env"
GENERATE_API_KEY=false
GENERATE_JWT_SECRET=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to generate a cryptographically secure random string
generate_secure_key() {
    local length=$1
    local prefix=$2
    
    # Try different methods based on what's available
    local key=""
    
    if command -v openssl >/dev/null 2>&1; then
        # Use OpenSSL (most reliable, available on most systems)
        key=$(openssl rand -base64 $((length * 3 / 4)) | tr -d "=+/" | cut -c1-${length})
    elif [[ -c /dev/urandom ]]; then
        # Use /dev/urandom with base64 encoding
        key=$(head -c $((length * 3 / 4)) /dev/urandom | base64 | tr -d "=+/\n" | cut -c1-${length})
    elif [[ -c /dev/random ]]; then
        # Fallback to /dev/random (may be slower)
        key=$(head -c $((length * 3 / 4)) /dev/random | base64 | tr -d "=+/\n" | cut -c1-${length})
    else
        print_color $RED "Error: No suitable random number generator found!"
        print_color $YELLOW "Please install openssl or ensure /dev/urandom is available."
        exit 1
    fi
    
    # Ensure we have the right length
    key=$(echo "$key" | cut -c1-${length})
    
    if [[ -n "$prefix" ]]; then
        echo "${prefix}-${key}"
    else
        echo "$key"
    fi
}

# Function to add or update key in .env file
add_to_env_file() {
    local key=$1
    local value=$2
    local file_path=$3
    local comment=$4
    
    local env_line="${key}=${value}"
    
    # Check if key already exists in file
    if [[ -f "$file_path" ]] && grep -q "^${key}=" "$file_path"; then
        print_color $YELLOW "Key '${key}' already exists in ${file_path}"
        read -p "Overwrite existing value? (y/N): " overwrite
        if [[ "$overwrite" =~ ^[Yy]$ ]]; then
            # Replace existing line (compatible with both macOS and Linux sed)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/^${key}=.*/${env_line}/" "$file_path"
            else
                # Linux
                sed -i "s/^${key}=.*/${env_line}/" "$file_path"
            fi
            print_color $GREEN "Updated ${key} in ${file_path}"
        else
            print_color $YELLOW "Skipping ${key}"
        fi
        return
    fi
    
    # Add new line
    if [[ -n "$comment" ]]; then
        echo "" >> "$file_path"
        echo "# $comment" >> "$file_path"
    fi
    echo "$env_line" >> "$file_path"
    print_color $GREEN "Added ${key} to ${file_path}"
}

# Function to show usage
show_usage() {
    echo ""
    echo "Usage:"
    echo "  ./generate_keys.sh --api-key          # Generate API key only"
    echo "  ./generate_keys.sh --jwt-secret       # Generate JWT secret only"
    echo "  ./generate_keys.sh --both             # Generate both keys"
    echo ""
    echo "Options:"
    echo "  --length <int>       # Key length (default: 64)"
    echo "  --env-file <string>  # .env file path (default: .env)"
    echo "  --help              # Show this help message"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            GENERATE_API_KEY=true
            shift
            ;;
        --jwt-secret)
            GENERATE_JWT_SECRET=true
            shift
            ;;
        --both)
            GENERATE_API_KEY=true
            GENERATE_JWT_SECRET=true
            shift
            ;;
        --length)
            LENGTH="$2"
            if ! [[ "$LENGTH" =~ ^[0-9]+$ ]] || [[ "$LENGTH" -lt 16 ]]; then
                print_color $RED "Error: Length must be a number >= 16"
                exit 1
            fi
            shift 2
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_color $RED "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main script logic
print_color $CYAN "🔐 BrainDrive Document AI - Key Generator"
print_color $CYAN "======================================="

# If no options provided, show interactive menu
if [[ "$GENERATE_API_KEY" == false ]] && [[ "$GENERATE_JWT_SECRET" == false ]]; then
    echo ""
    show_usage
    echo "What would you like to generate?"
    echo "1) API Key"
    echo "2) JWT Secret"
    echo "3) Both"
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            GENERATE_API_KEY=true
            ;;
        2)
            GENERATE_JWT_SECRET=true
            ;;
        3)
            GENERATE_API_KEY=true
            GENERATE_JWT_SECRET=true
            ;;
        *)
            print_color $RED "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

echo ""

# Check for required tools
if ! command -v openssl >/dev/null 2>&1 && [[ ! -c /dev/urandom ]] && [[ ! -c /dev/random ]]; then
    print_color $RED "Error: No suitable random number generator found!"
    print_color $YELLOW "Please install openssl or ensure /dev/urandom is available."
    print_color $YELLOW ""
    print_color $YELLOW "Installation instructions:"
    print_color $YELLOW "  macOS: brew install openssl"
    print_color $YELLOW "  Ubuntu/Debian: apt-get install openssl"
    print_color $YELLOW "  CentOS/RHEL: yum install openssl"
    exit 1
fi

# Generate API Key
if [[ "$GENERATE_API_KEY" == true ]]; then
    print_color $YELLOW "Generating API Key..."
    generated_api_key=$(generate_secure_key $LENGTH "sk")
    
    print_color $GREEN "✅ API Key generated:"
    print_color $WHITE "  $generated_api_key"
    echo ""
    
    # Option to save to .env file
    read -p "Save AUTH_API_KEY to $ENV_FILE? (y/N): " save
    if [[ "$save" =~ ^[Yy]$ ]]; then
        add_to_env_file "AUTH_API_KEY" "$generated_api_key" "$ENV_FILE" "Generated API key for BrainDrive Document AI"
    fi
    
    echo ""
    print_color $CYAN "🔧 Usage example:"
    print_color $GRAY "curl -X POST http://localhost:8000/documents/upload \\"
    print_color $GRAY "  -H \"X-API-Key: $generated_api_key\" \\"
    print_color $GRAY "  -F \"file=@document.pdf\""
    echo ""
fi

# Generate JWT Secret
if [[ "$GENERATE_JWT_SECRET" == true ]]; then
    print_color $YELLOW "Generating JWT Secret..."
    generated_jwt_secret=$(generate_secure_key $LENGTH)
    
    print_color $GREEN "✅ JWT Secret generated:"
    print_color $WHITE "  $generated_jwt_secret"
    echo ""
    
    # Option to save to .env file
    read -p "Save JWT_SECRET to $ENV_FILE? (y/N): " save
    if [[ "$save" =~ ^[Yy]$ ]]; then
        add_to_env_file "JWT_SECRET" "$generated_jwt_secret" "$ENV_FILE" "Generated JWT secret for BrainDrive Document AI"
    fi
    
    echo ""
    print_color $CYAN "🔧 JWT Token Generation (Python):"
    print_color $GRAY "import jwt"
    print_color $GRAY "from datetime import datetime, timedelta"
    echo ""
    print_color $GRAY "token = jwt.encode({"
    print_color $GRAY "    'sub': 'user123',"
    print_color $GRAY "    'exp': datetime.utcnow() + timedelta(hours=1)"
    print_color $GRAY "}, '$generated_jwt_secret', algorithm='HS256')"
    echo ""
fi

# Security recommendations
echo ""
print_color $CYAN "🛡️  Security Recommendations:"
print_color $WHITE "  • Store keys in environment variables, not in code"
print_color $WHITE "  • Use different keys for development and production"
print_color $WHITE "  • Rotate keys periodically"
print_color $WHITE "  • Never commit .env files to version control"
print_color $WHITE "  • Set DISABLE_AUTH=false in production"
echo ""

# .env file reminder
if [[ -f "$ENV_FILE" ]]; then
    print_color $CYAN "📝 Your $ENV_FILE file now contains:"
    echo ""
    grep -E "AUTH_API_KEY|JWT_SECRET|AUTH|DISABLE" "$ENV_FILE" 2>/dev/null | while read -r line; do
        if [[ "$line" =~ ^# ]]; then
            print_color $GRAY "  $line"
        else
            print_color $YELLOW "  $line"
        fi
    done || true
    echo ""
fi

print_color $GREEN "✨ Key generation complete!"

# Show platform-specific notes
echo ""
print_color $CYAN "📋 Platform Notes:"
case "$OSTYPE" in
    darwin*)
        print_color $WHITE "  • Running on macOS"
        print_color $WHITE "  • Using $(command -v openssl >/dev/null && echo "OpenSSL" || echo "/dev/urandom") for random generation"
        ;;
    linux*)
        print_color $WHITE "  • Running on Linux"
        print_color $WHITE "  • Using $(command -v openssl >/dev/null && echo "OpenSSL" || echo "/dev/urandom") for random generation"
        ;;
    *)
        print_color $WHITE "  • Running on $OSTYPE"
        print_color $WHITE "  • Using $(command -v openssl >/dev/null && echo "OpenSSL" || echo "/dev/urandom") for random generation"
        ;;
esac

echo ""
print_color $CYAN "🚀 Next Steps:"
print_color $WHITE "  1. Set DISABLE_AUTH=false in production"
print_color $WHITE "  2. Add your API key to client applications"
print_color $WHITE "  3. Test authentication with: curl -H \"X-API-Key: [your-key]\" [your-endpoint]"