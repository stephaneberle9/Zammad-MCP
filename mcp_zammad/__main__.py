"""Entry point for the Zammad MCP server."""

import logging
import sys

from .config import TransportConfig, TransportType
from .server import mcp

# Configure logging
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the MCP server with configured transport.

    Transport is configured via environment variables:
    - MCP_TRANSPORT: 'stdio' (default) or 'http'
    - MCP_HOST: Host for HTTP transport (default: 127.0.0.1)
    - MCP_PORT: Port for HTTP transport (default: 8000)
    """
    # Load transport configuration from environment
    config = TransportConfig.from_env()
    config.validate()

    try:
        # FastMCP handles its own async loop
        if config.transport == TransportType.HTTP:
            mcp.run(
                transport="http",
                host=config.host,
                port=config.port,
                uvicorn_config=config.get_uvicorn_config(),
            )
        else:
            mcp.run()
    except KeyboardInterrupt:
        # Graceful shutdown, suppress noisy logs resulting from asyncio.run task cancellation propagation
        pass
    except ValueError as e:
        # Configuration error, log w/o stack trace
        logger.error("Configuration error: %s", e)  # noqa: TRY400
        sys.exit(1)
    except RuntimeError as e:
        # Runtime error, log w/o stack trace
        logger.error("Runtime error: %s", e)  # noqa: TRY400
        sys.exit(1)
    except Exception as e:
        # Unexpected internal error, include full stack trace
        logger.error("Internal error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
