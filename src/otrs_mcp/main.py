#!/usr/bin/env python
import sys
import os
from otrs_mcp.server import mcp

def setup_environment():
    """Setup and validate environment configuration"""
    print("[CONFIG] OTRS MCP Server Configuration:")
    
    # Check required environment variables
    required_vars = ["OTRS_BASE_URL", "OTRS_USERNAME", "OTRS_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask password for display
            display_value = "*" * len(value) if "PASSWORD" in var else value
            print(f"  {var}: {display_value}")
    
    if missing_vars:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
        print("\n[INFO] Set these environment variables:")
        print("  export OTRS_BASE_URL='https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface'")
        print("  export OTRS_USERNAME='your-username'")
        print("  export OTRS_PASSWORD='your-password'")
        print("  export OTRS_VERIFY_SSL='false'  # Optional, for self-signed certificates")
        return False
    
    # Display optional configuration
    optional_vars = ["OTRS_VERIFY_SSL", "OTRS_DEFAULT_QUEUE", "OTRS_DEFAULT_STATE", "OTRS_DEFAULT_PRIORITY"]
    for var in optional_vars:
        value = os.getenv(var, "default")
        print(f"  {var}: {value}")
    
    return True

def run_server():
    """Main entry point for the OTRS MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    print("\n[START] Starting OTRS MCP Server...")
    print("[MODE] Running server in standard mode...")
    print("[OPS] Available operations: SessionCreate, TicketCreate, TicketGet, TicketSearch, TicketUpdate, TicketHistoryGet, ConfigItemGet, ConfigItemSearch")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()