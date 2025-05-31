#!/usr/bin/env python3
"""
Test OTRS API using the working TestInterface webservice
"""

import asyncio
import httpx
import json
import os

class OTRSTestClient:
    def __init__(self):
        self.base_url = os.getenv("OTRS_BASE_URL", "http://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface")
        self.username = os.getenv("OTRS_USERNAME", "seasonpoon.admin")
        self.password = os.getenv("OTRS_PASSWORD", "HOJTDVKm")
        self.verify_ssl = os.getenv("OTRS_VERIFY_SSL", "false").lower() == "true"
        self.default_queue = os.getenv("OTRS_DEFAULT_QUEUE", "Raw")
        self.default_state = os.getenv("OTRS_DEFAULT_STATE", "new")
        self.default_priority = os.getenv("OTRS_DEFAULT_PRIORITY", "3 normal")
        self.default_type = os.getenv("OTRS_DEFAULT_TYPE", "Unclassified")
        
        self.session_id = None
        self.session = None
        
        print(f"🔧 OTRS Client Configuration:")
        print(f"  Base URL: {self.base_url}")
        print(f"  Username: {self.username}")
        print(f"  SSL Verify: {self.verify_ssl}")
        print(f"  Default Queue: {self.default_queue}")
        print(f"  Default State: {self.default_state}")
        print(f"  Default Priority: {self.default_priority}")
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(verify=self.verify_ssl, timeout=30, follow_redirects=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def authenticate(self):
        """Authenticate and get session ID"""
        auth_url = f"{self.base_url}/SessionCreate"
        
        auth_data = {
            "UserLogin": self.username,
            "Password": self.password
        }
        
        try:
            response = await self.session.post(
                auth_url,
                json=auth_data,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            
            print(f"🔐 Authentication status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get("SessionID")
                if self.session_id:
                    print(f"✅ Authentication successful! SessionID: {self.session_id[:20]}...")
                    return True
                else:
                    print(f"❌ No SessionID in response: {result}")
                    return False
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    async def make_api_request(self, operation: str, data: dict = None):
        """Make an API request to OTRS"""
        if not self.session_id:
            if not await self.authenticate():
                raise Exception("Authentication failed")
        
        url = f"{self.base_url}/{operation}"
        
        request_data = {"SessionID": self.session_id}
        if data:
            request_data.update(data)
        
        try:
            response = await self.session.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            
            print(f"🔄 API Request: {operation} - Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {operation}")
                return result
            else:
                print(f"❌ API Error: {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            raise
    
    async def create_ticket(self, title: str, body: str, queue: str = None, customer_user: str = None):
        """Create a new ticket"""
        ticket_data = {
            "Ticket": {
                "Title": title,
                "Queue": queue or self.default_queue,
                "Priority": self.default_priority,
                "State": self.default_state,
                "Type": self.default_type,
                "CustomerUser": customer_user or self.username
            },
            "Article": {
                "Subject": title,
                "Body": body,
                "ContentType": "text/plain; charset=utf8",
                "ArticleType": "note-internal"
            }
        }
        
        return await self.make_api_request("TicketCreate", ticket_data)
    
    async def get_ticket(self, ticket_id: str):
        """Get ticket details"""
        ticket_data = {
            "TicketID": ticket_id,
            "DynamicFields": 1,
            "Extended": 1
        }
        
        return await self.make_api_request("TicketGet", ticket_data)
    
    async def search_tickets(self, limit: int = 10):
        """Search for tickets"""
        search_data = {
            "Limit": limit,
            "Result": "ARRAY",
            "SortBy": "Age",
            "OrderBy": "Down"
        }
        
        # Try different search criteria
        search_variations = [
            {"CustomerUserLogin": self.username, **search_data},
            {"UserID": 1, **search_data},  # Admin user
            {"StateType": "Open", **search_data},
            search_data  # Just basic search
        ]
        
        for i, search_params in enumerate(search_variations):
            print(f"🔍 Search attempt {i+1}: {list(search_params.keys())}")
            result = await self.make_api_request("TicketSearch", search_params)
            if result and not result.get("error"):
                return result
        
        return {"error": "All search attempts failed"}
    
    async def update_ticket(self, ticket_id: str, **updates):
        """Update a ticket"""
        update_data = {
            "TicketID": ticket_id,
            "Ticket": updates
        }
        
        return await self.make_api_request("TicketUpdate", update_data)

async def test_otrs_api():
    """Test the OTRS API functionality"""
    print("🚀 Testing OTRS API with TestInterface...")
    print("=" * 60)
    
    async with OTRSTestClient() as client:
        # Test authentication
        if await client.authenticate():
            
            # Test ticket search
            print("\n🔍 Testing ticket search...")
            search_result = await client.search_tickets()
            print(f"📊 Search result: {json.dumps(search_result, indent=2)}")
            
            # Test ticket creation
            print("\n🎫 Testing ticket creation...")
            create_result = await client.create_ticket(
                title="Test Ticket from API - " + str(asyncio.get_event_loop().time()),
                body="This is a test ticket created via the OTRS API using TestInterface webservice.\n\nTimestamp: " + str(asyncio.get_event_loop().time())
            )
            print(f"📝 Create result: {json.dumps(create_result, indent=2)}")
            
            # If ticket was created, try to get its details
            if create_result.get("TicketID"):
                ticket_id = create_result["TicketID"]
                print(f"\n📋 Testing ticket retrieval for ID: {ticket_id}...")
                get_result = await client.get_ticket(str(ticket_id))
                print(f"📄 Get result: {json.dumps(get_result, indent=2)}")
                
                # Test ticket update
                print(f"\n✏️ Testing ticket update for ID: {ticket_id}...")
                update_result = await client.update_ticket(
                    str(ticket_id),
                    State="open",
                    Priority="4 high"
                )
                print(f"🔄 Update result: {json.dumps(update_result, indent=2)}")
            
            print("\n✅ All tests completed!")
        else:
            print("❌ Authentication failed - cannot proceed with tests")

if __name__ == "__main__":
    print("🌍 OTRS API Test Suite")
    print("=" * 60)
    print("Environment Variables (set these to customize):")
    print("  OTRS_BASE_URL - Base URL for OTRS webservice")
    print("  OTRS_USERNAME - OTRS username")
    print("  OTRS_PASSWORD - OTRS password")
    print("  OTRS_VERIFY_SSL - true/false for SSL verification")
    print("  OTRS_DEFAULT_QUEUE - Default queue name")
    print("  OTRS_DEFAULT_STATE - Default ticket state")
    print("  OTRS_DEFAULT_PRIORITY - Default priority")
    print("  OTRS_DEFAULT_TYPE - Default ticket type")
    print("=" * 60)
    
    asyncio.run(test_otrs_api())