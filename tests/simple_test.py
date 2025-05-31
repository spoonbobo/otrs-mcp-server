#!/usr/bin/env python3
"""
Simplified OTRS test with HTTPS support
"""

import asyncio
import httpx
import os

async def simple_test():
    print("🚀 Simple OTRS Test with HTTPS Support")
    
    # Test both HTTP and HTTPS
    base_http = os.getenv("OTRS_BASE_URL", "http://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface")
    base_https = base_http.replace("http://", "https://")
    
    username = os.getenv("OTRS_USERNAME", "seasonpoon.admin")
    password = os.getenv("OTRS_PASSWORD", "HOJTDVKm")
    
    for base_url in [base_http, base_https]:
        print(f"\n🔗 Testing: {base_url}")
        print(f"Username: {username}")
        
        # Test with SSL verification disabled and follow redirects
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30) as client:
            # Test GET
            try:
                response = await client.get(base_url)
                print(f"  GET Status: {response.status_code}")
                print(f"  Final URL: {response.url}")
            except Exception as e:
                print(f"  GET Error: {e}")
                continue
            
            # Test POST auth
            try:
                response = await client.post(
                    f"{base_url}/SessionCreate",
                    json={"UserLogin": username, "Password": password},
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                )
                print(f"  POST Status: {response.status_code}")
                print(f"  Final URL: {response.url}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        session_id = result.get("SessionID")
                        if session_id:
                            print(f"  🎉 SUCCESS! SessionID: {session_id[:20]}...")
                            return base_url
                        else:
                            print(f"  Response: {result}")
                    except:
                        print(f"  Response (not JSON): {response.text[:200]}...")
                else:
                    print(f"  Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"  POST Error: {e}")

if __name__ == "__main__":
    working_url = asyncio.run(simple_test())
    if working_url:
        print(f"\n✅ Working URL: {working_url}")
        print(f"💡 Set this as your OTRS_BASE_URL environment variable") 