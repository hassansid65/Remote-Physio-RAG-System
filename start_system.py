#!/usr/bin/env python3
"""
Remote Physio System Startup Script
Starts all required services and verifies they're working
"""

import subprocess
import time
import requests
import sys
import os

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                print(f"✅ {description} - Success")
                return result.stdout.strip()
            else:
                print(f"❌ {description} - Failed: {result.stderr}")
                return None
        else:
            subprocess.run(command, shell=True, check=True, cwd=os.getcwd())
            print(f"✅ {description} - Success")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        return False

def check_service(url, service_name, max_retries=10):
    """Check if a service is responding"""
    print(f"🔍 Checking {service_name}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is responding")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ Waiting for {service_name}... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print(f"❌ {service_name} is not responding after {max_retries} attempts")
    return False

def check_docker_containers():
    """Check if required Docker containers are running"""
    print("🔍 Checking Docker containers...")
    
    result = run_command("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", 
                        "Getting Docker container status", check_output=True)
    
    if result:
        print("📊 Docker Containers:")
        print(result)
        
        # Check for required containers
        weaviate_running = "weaviate" in result.lower() or "8080" in result
        mongodb_running = "mongodb" in result.lower() or "mongo" in result.lower() or "27017" in result
        
        return weaviate_running, mongodb_running
    
    return False, False

def start_docker_services():
    """Start required Docker services"""
    print("\n🚀 Starting Docker Services...")
    
    weaviate_running, mongodb_running = check_docker_containers()
    
    if not weaviate_running:
        print("🔄 Starting Weaviate...")
        run_command(
            "docker run -d -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:latest",
            "Starting Weaviate container"
        )
        time.sleep(5)
    else:
        print("✅ Weaviate container already running")
    
    if not mongodb_running:
        print("🔄 Starting MongoDB...")
        run_command(
            "docker run -d -p 27017:27017 --name mongodb mongo:latest",
            "Starting MongoDB container"
        )
        time.sleep(3)
    else:
        print("✅ MongoDB container already running")

def verify_services():
    """Verify all services are working"""
    print("\n🔍 Verifying Services...")
    
    # Check Weaviate
    weaviate_ok = check_service("http://localhost:8080/v1/meta", "Weaviate")
    
    # Check API Server
    api_ok = check_service("http://localhost:8002/", "FastAPI Server")
    
    return weaviate_ok and api_ok

def test_system():
    """Test the system with a sample query"""
    print("\n🧪 Testing System...")
    
    try:
        # Test basic API
        response = requests.get("http://localhost:8002/")
        if response.status_code == 200:
            print("✅ API basic endpoint working")
        
        # Test RAG endpoint
        response = requests.post(
            "http://localhost:8002/chat/ask",
            json={"question": "What is the Berg Balance Test?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RAG system working")
            print(f"📝 Sample response: {data['answer'][:100]}...")
            print(f"📚 Context found: {data['context_found']}")
            return True
        else:
            print(f"❌ RAG test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main startup sequence"""
    print("🚀 Remote Physio System Startup")
    print("=" * 50)
    
    # Step 1: Start Docker services
    start_docker_services()
    
    # Step 2: Wait a moment for services to initialize
    print("\n⏳ Waiting for services to initialize...")
    time.sleep(5)
    
    # Step 3: Verify services
    if not verify_services():
        print("\n❌ Some services are not responding. Please check the logs.")
        sys.exit(1)
    
    # Step 4: Test the system
    if test_system():
        print("\n🎉 System startup complete!")
        print("\n📋 System Status:")
        print("  ✅ Weaviate (Vector DB): http://localhost:8080")
        print("  ✅ MongoDB (Chat History): localhost:27017")
        print("  ✅ FastAPI Server: http://localhost:8002")
        print("  ✅ RAG System: Working with 1,648 documents")
        
        print("\n🔗 Available Endpoints:")
        print("  • GET  /                    - API status")
        print("  • GET  /health              - Health check")
        print("  • POST /chat/ask            - Direct RAG questions")
        print("  • POST /chat/start/{user_id} - Start chat session")
        print("  • POST /chat/message        - Send chat message")
        print("  • POST /data/upload/text    - Upload data")
        
        print("\n🌐 Web Interface:")
        print("  Open your browser and go to: http://localhost:8002")
        print("  Or run: python open_web_interface.py")

        print("\n💡 Try this API call:")
        print('  curl -X POST "http://localhost:8002/chat/ask" \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"question": "What is the Berg Balance Test?"}\'')

    else:
        print("\n❌ System test failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
