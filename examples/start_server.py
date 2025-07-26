#!/usr/bin/env python3
"""
MCP Server Startup Script

This script starts the MCP server and keeps it running.
Use Ctrl+C to gracefully shutdown the server.
"""

import asyncio
import sys
import os
import signal
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.mcp_server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Start the MCP server"""
    server = MCPServer()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        raise KeyboardInterrupt()
    
    # Register signal handlers
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    
    try:
        logger.info("Starting MCP Server...")
        logger.info("Press Ctrl+C to stop the server")
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.shutdown()
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    print("=== MCP Server ===")
    print("Model Context Protocol Server for Application Usage Tracking")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
