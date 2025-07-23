import sys
import os
import asyncio
import logging

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from mcp.mcp_server import MCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the application.
    Initializes and starts the MCP server.
    """
    logger.info("Starting the Application...")
    server = MCPServer()

    try:
        logger.info("Launching MCP Server...")
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Application shutting down gracefully.")
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)

if __name__ == '__main__':
    main()
