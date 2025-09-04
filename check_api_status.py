#!/usr/bin/env python3
"""
API Status Checker
-----------------
This script checks the status of your Google Generative AI API
and reports on quota limitations and errors.
"""

import os
import time
from dotenv import load_dotenv
import requests
import json
from typing import Dict, Any

# Load environment variables
load_dotenv()

def print_section(title: str) -> None:
    """Print a formatted section title"""
    print("\n" + "=" * 50)
    print(f" {title} ")
    print("=" * 50)

def check_api_key() -> bool:
    """Check if API key is properly configured"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: Google API Key not found in environment variables")
        print("  Make sure your .env file has a GOOGLE_API_KEY entry")
        return False
    
    print(f"✅ API Key configured: {api_key[:4]}...{api_key[-4:]}")
    return True

def check_local_server() -> Dict[str, Any]:
    """Check if local API server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Local server is running: {data.get('status', 'unknown')}")
        return {"status": "running", "data": data}
    except requests.exceptions.ConnectionError:
        print("❌ Local server is not running")
        print("  Start it with: uvicorn main:app --reload")
        return {"status": "not_running"}
    except Exception as e:
        print(f"❌ Error checking local server: {str(e)}")
        return {"status": "error", "error": str(e)}

def check_api_status() -> Dict[str, Any]:
    """Check API status using the local server's api-status endpoint"""
    try:
        response = requests.get("http://localhost:8000/api-status", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "operational":
            print(f"✅ API is operational")
            print(f"  Model: {data.get('model', 'unknown')}")
            print(f"  Response time: {data.get('response_time_seconds', 'unknown')} seconds")
            print(f"  Tier: {data.get('api_tier', 'unknown')}")
        else:
            print(f"❌ API is not operational: {data.get('status', 'unknown')}")
            if "error" in data:
                print(f"  Error: {data.get('error')}")
        
        return {"status": "checked", "data": data}
    except requests.exceptions.ConnectionError:
        print("❌ Cannot check API status - local server is not running")
        return {"status": "server_not_running"}
    except Exception as e:
        print(f"❌ Error checking API status: {str(e)}")
        return {"status": "error", "error": str(e)}

def check_chat_endpoint() -> Dict[str, Any]:
    """Test the chat endpoint with a simple message"""
    try:
        print("Sending test message to chat endpoint...")
        response = requests.post(
            "http://localhost:8000/chat", 
            json={"message": "Hello, just testing the API status"}, 
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat endpoint is working")
            print(f"  Response: {data.get('reply', 'unknown')[:50]}...")
            return {"status": "working", "data": data}
        elif response.status_code == 429:
            data = response.json()
            print(f"❌ Rate limit or quota exceeded")
            print(f"  Error: {data.get('detail', 'unknown')}")
            return {"status": "rate_limited", "data": data}
        else:
            data = response.json() if response.content else {}
            print(f"❌ Chat endpoint error: Status {response.status_code}")
            if "detail" in data:
                print(f"  Details: {data.get('detail')}")
            return {"status": "error", "code": response.status_code, "data": data}
    except requests.exceptions.ConnectionError:
        print("❌ Cannot test chat endpoint - local server is not running")
        return {"status": "server_not_running"}
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {str(e)}")
        return {"status": "error", "error": str(e)}

def print_recommendations(results: Dict[str, Any]) -> None:
    """Print recommendations based on test results"""
    print_section("RECOMMENDATIONS")
    
    # Check for rate limit/quota issues
    api_status = results.get("api_status", {}).get("data", {})
    chat_status = results.get("chat_status", {})
    
    if (api_status.get("status") != "operational" or 
        chat_status.get("status") in ["rate_limited", "error"]):
        
        print("📊 QUOTA/RATE LIMIT RECOMMENDATIONS:")
        print("  1. Wait a few minutes before trying again")
        print("  2. Check your quota at: https://ai.google.dev/pricing")
        print("  3. Consider upgrading your API tier")
        print("  4. Try using a different model (currently using: " + 
              f"{api_status.get('model', 'unknown')})")
        print("  5. Implement rate limiting in your application")
        
    if results.get("local_server", {}).get("status") != "running":
        print("🖥️ SERVER RECOMMENDATIONS:")
        print("  1. Start the server with: uvicorn main:app --reload")
        print("  2. Check for any error messages during server startup")

    print("\nFor more information on Google AI API limits, visit:")
    print("https://ai.google.dev/gemini-api/docs/rate-limits")

def main() -> None:
    """Main function to check API status"""
    print_section("GOOGLE GENERATIVE AI API STATUS CHECK")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Check API key
    api_key_status = check_api_key()
    results["api_key"] = {"status": "configured" if api_key_status else "missing"}
    
    # Only proceed with other checks if API key is configured
    if api_key_status:
        # Check local server
        results["local_server"] = check_local_server()
        
        # Only check API status if local server is running
        if results["local_server"]["status"] == "running":
            results["api_status"] = check_api_status()
            
            # Only test chat endpoint if API status check didn't show problems
            api_data = results.get("api_status", {}).get("data", {})
            if api_data.get("status") == "operational":
                print("\nTesting chat endpoint...")
                results["chat_status"] = check_chat_endpoint()
    
    # Print recommendations
    print_recommendations(results)
    
    print_section("END OF STATUS CHECK")

if __name__ == "__main__":
    main()
