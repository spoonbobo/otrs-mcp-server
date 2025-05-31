#!/usr/bin/env python3
"""
Simple OTRS connectivity test to diagnose API endpoint issues
"""

import asyncio
import httpx
import os

async def test_connectivity():
    # Get configuration from environment variables
    base_url = os.getenv("OTRS_BASE_URL", "http://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface")
    username = os.getenv("OTRS_USERNAME", "seasonpoon.admin")
    password = os.getenv("OTRS_PASSWORD", "HOJTDVKm")
    verify_ssl = os.getenv("OTRS_VERIFY_SSL", "false").lower() == "true"
    
    print(f"🔧 Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Username: {username}")
    print(f"  SSL Verify: {verify_ssl}")
    
    # Test multiple potential endpoints
    test_urls = [
        base_url,
        base_url.replace("TestInterface", "GenericTicketConnectorREST"),
        base_url.replace("TestInterface", "GenericTicketConnector"),
    ]
    
    # Also test both HTTP and HTTPS if not explicitly set
    if "OTRS_BASE_URL" not in os.environ:
        https_url = base_url.replace("http://", "https://")
        if https_url != base_url:
            test_urls.append(https_url)
    
    async with httpx.AsyncClient(verify=verify_ssl, timeout=10, follow_redirects=True) as client:
        for test_url in test_urls:
            print(f"\n🔍 Testing: {test_url}")
            
            # Test basic connectivity
            try:
                response = await client.get(test_url)
                print(f"  ✅ GET {test_url} - Status: {response.status_code}")
                print(f"  🔗 Final URL: {response.url}")
                if response.text:
                    print(f"  📄 Response preview: {response.text[:200]}...")
            except Exception as e:
                print(f"  ❌ GET failed: {str(e)}")
            
            # Test authentication endpoint
            auth_url = f"{test_url}/SessionCreate"
            try:
                response = await client.post(
                    auth_url,
                    json={"UserLogin": username, "Password": password},
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                )
                print(f"  ✅ POST {auth_url} - Status: {response.status_code}")
                print(f"  🔗 Final URL: {response.url}")
                if response.text:
                    print(f"  📄 Auth response: {response.text[:300]}...")
            except Exception as e:
                print(f"  ❌ POST auth failed: {str(e)}")
            
            # Test alternative auth formats
            for auth_endpoint in ["/customer/auth/login", "/auth", "/login"]:
                alt_auth_url = f"{test_url}{auth_endpoint}"
                try:
                    response = await client.post(
                        alt_auth_url,
                        json={"Username": username, "Password": password, "UserLogin": username},
                        headers={"Content-Type": "application/json", "Accept": "application/json"}
                    )
                    print(f"  ✅ POST {alt_auth_url} - Status: {response.status_code}")
                    if response.text:
                        print(f"  📄 Alt auth response: {response.text[:200]}...")
                except Exception as e:
                    print(f"  ❌ POST alt auth failed: {str(e)}")

if __name__ == "__main__":
    print("🌍 OTRS Connectivity Test")
    print("=" * 50)
    print("Set these environment variables to customize:")
    print("  OTRS_BASE_URL - Base URL for OTRS webservice")
    print("  OTRS_USERNAME - OTRS username")
    print("  OTRS_PASSWORD - OTRS password")
    print("  OTRS_VERIFY_SSL - true/false for SSL verification")
    print("=" * 50)
    
    asyncio.run(test_connectivity())