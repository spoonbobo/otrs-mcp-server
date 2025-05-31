#!/usr/bin/env python3
"""
Debug script to identify what's not working
"""

import asyncio
import httpx
import os
import sys
import traceback

async def debug_test():
    print("🔍 OTRS Debug Test")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    print("\n🌍 Environment Variables:")
    env_vars = ["OTRS_BASE_URL", "OTRS_USERNAME", "OTRS_PASSWORD", "OTRS_VERIFY_SSL"]
    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        if "PASSWORD" in var and value != "NOT SET":
            value = "*" * len(value)
        print(f"  {var}: {value}")
    
    # Test both HTTP and HTTPS
    base_urls = [
        os.getenv("OTRS_BASE_URL", "http://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface"),
        os.getenv("OTRS_BASE_URL", "http://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface").replace("http://", "https://")
    ]
    
    for base_url in base_urls:
        print(f"\n🔗 Testing: {base_url}")
        
        # Test basic HTTP client
        try:
            async with httpx.AsyncClient(verify=False, timeout=10, follow_redirects=True) as client:
                print("  ✅ HTTP client created successfully")
                
                # Test basic connectivity
                try:
                    response = await client.get(base_url)
                    print(f"  ✅ GET request - Status: {response.status_code}")
                    print(f"  🔗 Final URL: {response.url}")
                    print(f"  📄 Response length: {len(response.text)} characters")
                    
                    if response.status_code != 200:
                        print(f"  📄 Response preview: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"  ❌ GET request failed: {str(e)}")
                    continue
                
                # Test authentication
                print(f"  🔐 Testing authentication:")
                auth_url = f"{base_url}/SessionCreate"
                auth_data = {
                    "UserLogin": os.getenv("OTRS_USERNAME", "seasonpoon.admin"),
                    "Password": os.getenv("OTRS_PASSWORD", "HOJTDVKm")
                }
                
                try:
                    response = await client.post(
                        auth_url,
                        json=auth_data,
                        headers={"Content-Type": "application/json", "Accept": "application/json"}
                    )
                    print(f"  ✅ POST request - Status: {response.status_code}")
                    print(f"  🔗 Final URL: {response.url}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            session_id = result.get("SessionID")
                            if session_id:
                                print(f"  🎉 Authentication successful! SessionID: {session_id[:20]}...")
                                return base_url  # Return the working URL
                            else:
                                print(f"  ⚠️ No SessionID in response: {result}")
                        except:
                            print(f"  ⚠️ Response is not JSON: {response.text[:200]}...")
                    else:
                        print(f"  📄 Response: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"  ❌ POST request failed: {str(e)}")
                    
        except Exception as e:
            print(f"  ❌ Failed to create HTTP client: {str(e)}")

if __name__ == "__main__":
    try:
        working_url = asyncio.run(debug_test())
        if working_url:
            print(f"\n🎉 Working URL found: {working_url}")
            print(f"💡 Update your OTRS_BASE_URL to: {working_url}")
    except Exception as e:
        print(f"❌ Script failed to run: {str(e)}")
        traceback.print_exc() 