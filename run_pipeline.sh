#!/bin/bash

# Unix Shell Script for SRT-to-Audio Pipeline
# This script provides a simple interface for Unix-like systems

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PS_SCRIPT="$SCRIPT_DIR/run_pipeline.ps1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}%s${NC}\n" "$2"
}

# Check if PowerShell is available
check_powershell() {
    if command -v pwsh >/dev/null 2>&1; then
        PS_CMD="pwsh"
    elif command -v powershell >/dev/null 2>&1; then
        PS_CMD="powershell"
    else
        print_color "$RED" "❌ PowerShell not found. Please install PowerShell Core."
        print_color "$YELLOW" "💡 Installation instructions:"
        print_color "$YELLOW" "   - Ubuntu/Debian: snap install powershell --classic"
        print_color "$YELLOW" "   - CentOS/RHEL: Download from https://github.com/PowerShell/PowerShell"
        print_color "$YELLOW" "   - macOS: brew install powershell"
        exit 1
    fi
}

# Show usage
show_usage() {
    print_color "$CYAN" "Usage: $0 <audio_file> [whisper_model] [output_file]"
    echo ""
    print_color "$YELLOW" "Examples:"
    print_color "$YELLOW" "  $0 my_audio.mp3"
    print_color "$YELLOW" "  $0 my_audio.wav large"
    print_color "$YELLOW" "  $0 my_audio.mp3 medium my_output.mp3"
    echo ""
    print_color "$YELLOW" "Whisper Models: tiny, base, small, medium, large"
}

# Main execution
main() {
    print_color "$CYAN" "🚀 SRT-to-Audio Pipeline (Unix Wrapper)"
    print_color "$CYAN" "======================================"
    
    # Check arguments
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    # Check PowerShell
    check_powershell
    
    # Check if input file exists
    if [ ! -f "$1" ]; then
        print_color "$RED" "❌ Input audio file not found: $1"
        exit 1
    fi
    
    # Build PowerShell arguments
    PS_ARGS=("-InputAudioFile" "$1")
    
    if [ $# -ge 2 ] && [ -n "$2" ]; then
        PS_ARGS+=("-WhisperModel" "$2")
    fi
    
    if [ $# -ge 3 ] && [ -n "$3" ]; then
        PS_ARGS+=("-OutputAudio" "$3")
    fi
    
    print_color "$CYAN" "🔧 Executing PowerShell script..."
    print_color "$YELLOW" "Command: $PS_CMD -File \"$PS_SCRIPT\" ${PS_ARGS[*]}"
    echo ""
    
    # Execute PowerShell script
    "$PS_CMD" -File "$PS_SCRIPT" "${PS_ARGS[@]}"
    
    # Check exit code
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        print_color "$RED" "❌ Pipeline failed with exit code $exit_code"
        exit $exit_code
    fi
    
    print_color "$GREEN" "🎉 Pipeline completed successfully!"
}

# Run main function with all arguments
main "$@"