#!/usr/bin/env python3
"""
Simple system test for Remote Physio RAG System
Tests basic functionality to ensure everything is working
"""

import requests
import sys

def test_api_status():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8002/api", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_web_interface():
    """Test if the web interface is accessible"""
    try:
        response = requests.get("http://localhost:8002/", timeout=5)
        if response.status_code == 200 and "Anu - AI Physio Assistant" in response.text:
            print("✅ Web interface is accessible")
            return True
        else:
            print("❌ Web interface not accessible")
            return False
    except Exception as e:
        print(f"❌ Web interface connection failed: {e}")
        return False

def test_rag_system():
    """Test the RAG system with a sample question"""
    try:
        response = requests.post(
            "http://localhost:8002/chat/ask",
            json={"question": "What is the Berg Balance Test?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('context_found') and len(data.get('answer', '')) > 50:
                print("✅ RAG system is working")
                print(f"📝 Sample answer: {data['answer'][:100]}...")
                return True
            else:
                print("❌ RAG system returned incomplete response")
                return False
        else:
            print(f"❌ RAG system returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("🧪 Testing Remote Physio System...")
    print("=" * 50)
    
    tests = [
        ("API Status", test_api_status),
        ("Web Interface", test_web_interface),
        ("RAG System", test_rag_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"💡 Make sure the server is running: python -m uvicorn backend.app:app --host 0.0.0.0 --port 8002 --reload")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems working! Your Remote Physio system is ready to use.")
        print("🌐 Open http://localhost:8002 in your browser to start chatting!")
    else:
        print("❌ Some tests failed. Please check the server status.")
        sys.exit(1)

if __name__ == "__main__":
    main()
