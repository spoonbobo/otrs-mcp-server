#!/usr/bin/env python

import os
import json
import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import httpx

import dotenv
from mcp.server.fastmcp import FastMCP

dotenv.load_dotenv()
mcp = FastMCP("OTRS API MCP")

@dataclass
class OTRSConfig:
    base_url: str = os.getenv("OTRS_BASE_URL", "https://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface")
    username: str = os.getenv("OTRS_USERNAME", "seasonpoon.admin")
    password: str = os.getenv("OTRS_PASSWORD", "HOJTDVKm")
    verify_ssl: bool = os.getenv("OTRS_VERIFY_SSL", "false").lower() == "true"
    default_queue: str = os.getenv("OTRS_DEFAULT_QUEUE", "Raw")
    default_state: str = os.getenv("OTRS_DEFAULT_STATE", "new")
    default_priority: str = os.getenv("OTRS_DEFAULT_PRIORITY", "3 normal")
    default_type: str = os.getenv("OTRS_DEFAULT_TYPE", "Unclassified")

config = OTRSConfig()

async def make_api_request(endpoint: str, data: Dict[str, Any] = None, use_session: bool = True) -> Dict[str, Any]: # type: ignore

    """Make API request to OTRS""" 
    url = f"{config.base_url}/{endpoint}"
    
    # Default data structure for OTRS
    if data is None:
        data = {}
    
    # Add authentication (for non-session operations or when session is not available)
    if not use_session or endpoint == "SessionCreate":
        data.update({
            "UserLogin": config.username,
            "Password": config.password
        })
    
    async with httpx.AsyncClient(verify=config.verify_ssl, follow_redirects=True, timeout=30) as client:
        response = await client.post(
            url, 
            json=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()

# Session Management
@mcp.tool(description="Create a new OTRS session")
async def create_session() -> Dict[str, Any]:
    """
    Create a new session in OTRS.
    
    Returns:
    - SessionID and session information
    """
    return await make_api_request("SessionCreate")

# Ticket Operations
@mcp.tool(description="Create a new ticket in OTRS")
async def create_ticket(
    title: str,
    body: str,
    queue: Optional[str] = None,
    priority: Optional[str] = None,
    state: Optional[str] = None,
    customer_user: Optional[str] = None,
    ticket_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new ticket in OTRS.
    
    Parameters:
    - title: Ticket title/subject
    - body: Ticket body content
    - queue: Queue name (optional, defaults to configured default)
    - priority: Priority level (optional, defaults to configured default)
    - state: Ticket state (optional, defaults to configured default)
    - customer_user: Customer user login (optional, defaults to current user)
    - ticket_type: Ticket type (optional, defaults to configured default)
    """
    ticket_data = {
        "Ticket": {
            "Title": title,
            "Queue": queue or config.default_queue,
            "Priority": priority or config.default_priority,
            "State": state or config.default_state,
            "Type": ticket_type or config.default_type,
            "CustomerUser": customer_user or config.username
        },
        "Article": {
            "Subject": title,
            "Body": body,
            "ContentType": "text/plain; charset=utf8",
            "ArticleType": "note-internal"
        }
    }
    
    return await make_api_request("TicketCreate", ticket_data, use_session=False)

@mcp.tool(description="Get ticket details from OTRS")
async def get_ticket(
    ticket_id: str,
    include_dynamic_fields: bool = True,
    include_extended_data: bool = True
) -> Dict[str, Any]:
    """
    Get detailed information about a specific ticket.
    
    Parameters:
    - ticket_id: The ticket ID to retrieve
    - include_dynamic_fields: Include dynamic field data
    - include_extended_data: Include extended ticket information
    """
    ticket_data = {
        "TicketID": ticket_id,
        "DynamicFields": 1 if include_dynamic_fields else 0,
        "Extended": 1 if include_extended_data else 0
    }
    
    return await make_api_request("TicketGet", ticket_data, use_session=False)

@mcp.tool(description="Search for tickets in OTRS")
async def search_tickets(
    customer_user: Optional[str] = None,
    queue: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    title: Optional[str] = None,
    limit: int = 50,
    sort_by: str = "Age",
    order_by: str = "Down"
) -> Dict[str, Any]:
    """
    Search for tickets in OTRS based on various criteria.
    
    Parameters:
    - customer_user: Filter by customer user login
    - queue: Filter by queue name
    - state: Filter by ticket state
    - priority: Filter by priority
    - title: Search in ticket titles
    - limit: Maximum number of results (default: 50)
    - sort_by: Sort field (Age, Created, etc.)
    - order_by: Sort order (Up/Down)
    """
    search_data = {
        "Limit": limit,
        "Result": "ARRAY",
        "SortBy": sort_by,
        "OrderBy": order_by
    }
    
    # Add search criteria
    if customer_user:
        search_data["CustomerUserLogin"] = customer_user
    if queue:
        search_data["Queues"] = [queue]
    if state:
        search_data["States"] = [state]
    if priority:
        search_data["Priorities"] = [priority]
    if title:
        search_data["Title"] = title
    
    return await make_api_request("TicketSearch", search_data, use_session=False)

@mcp.tool(description="Update an existing ticket in OTRS")
async def update_ticket(
    ticket_id: str,
    title: Optional[str] = None,
    queue: Optional[str] = None,
    priority: Optional[str] = None,
    state: Optional[str] = None,
    customer_user: Optional[str] = None,
    owner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing ticket in OTRS.
    
    Parameters:
    - ticket_id: The ticket ID to update
    - title: New ticket title
    - queue: New queue name
    - priority: New priority level
    - state: New ticket state
    - customer_user: New customer user
    - owner: New ticket owner
    """
    update_data = {
        "TicketID": ticket_id,
        "Ticket": {}
    }
    
    # Add fields to update
    if title:
        update_data["Ticket"]["Title"] = title
    if queue:
        update_data["Ticket"]["Queue"] = queue
    if priority:
        update_data["Ticket"]["Priority"] = priority
    if state:
        update_data["Ticket"]["State"] = state
    if customer_user:
        update_data["Ticket"]["CustomerUser"] = customer_user
    if owner:
        update_data["Ticket"]["Owner"] = owner
    
    return await make_api_request("TicketUpdate", update_data, use_session=False)

@mcp.tool(description="Get ticket history from OTRS")
async def get_ticket_history(
    ticket_id: str
) -> Dict[str, Any]:
    """
    Get the history of a specific ticket.
    
    Parameters:
    - ticket_id: The ticket ID to get history for
    """
    history_data = {
        "TicketID": ticket_id
    }
    
    return await make_api_request("TicketHistoryGet", history_data, use_session=False)

# Configuration Item Operations
@mcp.tool(description="Get configuration item details from OTRS")
async def get_config_item(
    config_item_id: str,
    include_dynamic_fields: bool = True
) -> Dict[str, Any]:
    """
    Get detailed information about a specific configuration item.
    
    Parameters:
    - config_item_id: The configuration item ID to retrieve
    - include_dynamic_fields: Include dynamic field data
    """
    ci_data = {
        "ConfigItemID": config_item_id,
        "DynamicFields": 1 if include_dynamic_fields else 0
    }
    
    return await make_api_request("ConfigItemGet", ci_data, use_session=False)

@mcp.tool(description="Search for configuration items in OTRS")
async def search_config_items(
    name: Optional[str] = None,
    class_name: Optional[str] = None,
    deployment_state: Optional[str] = None,
    incident_state: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Search for configuration items in OTRS.
    
    Parameters:
    - name: Filter by configuration item name
    - class_name: Filter by class name
    - deployment_state: Filter by deployment state
    - incident_state: Filter by incident state
    - limit: Maximum number of results (default: 50)
    """
    search_data = {
        "Limit": limit,
        "Result": "ARRAY"
    }
    
    # Add search criteria
    if name:
        search_data["Name"] = name
    if class_name:
        search_data["ClassIDs"] = [class_name]
    if deployment_state:
        search_data["DeplStateIDs"] = [deployment_state]
    if incident_state:
        search_data["InciStateIDs"] = [incident_state]
    
    return await make_api_request("ConfigItemSearch", search_data, use_session=False)

# Resources for easy data access
@mcp.resource("otrs://ticket/{ticket_id}")
async def ticket_resource(ticket_id: str) -> str:
    """
    Resource that returns ticket data.
    
    Parameters:
    - ticket_id: The ticket ID
    """
    try:
        ticket = await get_ticket(ticket_id=ticket_id)
        return json.dumps(ticket, indent=2)
    except Exception as e:
        return f"Error retrieving ticket: {str(e)}"

@mcp.resource("otrs://ticket/{ticket_id}/history")
async def ticket_history_resource(ticket_id: str) -> str:
    """
    Resource that returns ticket history.
    
    Parameters:
    - ticket_id: The ticket ID
    """
    try:
        history = await get_ticket_history(ticket_id=ticket_id)
        return json.dumps(history, indent=2)
    except Exception as e:
        return f"Error retrieving ticket history: {str(e)}"

@mcp.resource("otrs://search/tickets")
async def search_tickets_resource() -> str:
    """
    Resource that returns recent tickets.
    """
    try:
        tickets = await search_tickets(limit=20)
        return json.dumps(tickets, indent=2)
    except Exception as e:
        return f"Error searching tickets: {str(e)}"

@mcp.resource("otrs://configitem/{config_item_id}")
async def config_item_resource(config_item_id: str) -> str:
    """
    Resource that returns configuration item data.
    
    Parameters:
    - config_item_id: The configuration item ID
    """
    try:
        config_item = await get_config_item(config_item_id=config_item_id)
        return json.dumps(config_item, indent=2)
    except Exception as e:
        return f"Error retrieving configuration item: {str(e)}"

if __name__ == "__main__":
    print(f"🚀 Starting OTRS MCP Server...")
    mcp.run()