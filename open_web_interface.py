#!/usr/bin/env python3
"""
Open the Remote Physio Web Interface
"""

import webbrowser
import time
import requests
import sys

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8002/api", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🌐 Opening Remote Physio Web Interface...")
    
    # Check if server is running
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  python start_system.py")
        print("  OR")
        print("  python -m uvicorn backend.app:app --host 0.0.0.0 --port 8002 --reload")
        sys.exit(1)
    
    print("✅ Server is running")
    print("🚀 Opening web interface at http://localhost:8002")
    
    # Open the web interface
    webbrowser.open("http://localhost:8002")
    
    print("\n📋 Web Interface Features:")
    print("  • Chat with the AI physiotherapy assistant")
    print("  • Ask questions about assessments and exercises")
    print("  • Get evidence-based physiotherapy advice")
    print("  • Access to 1,648 physiotherapy documents")
    
    print("\n💡 Try asking:")
    print("  • 'What is the Berg Balance Test?'")
    print("  • 'I have back pain, what should I do?'")
    print("  • 'Show me shoulder strengthening exercises'")

if __name__ == "__main__":
    main()
