# Zammad MCP Server

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/basher83/Zammad-MCP?utm_source=oss&utm_medium=github&utm_campaign=basher83%2FZammad-MCP&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9cc0ebac926a4d56b0bdf2271d46bbf7)](https://app.codacy.com/gh/basher83/Zammad-MCP/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Coverage](https://app.codacy.com/project/badge/Coverage/9cc0ebac926a4d56b0bdf2271d46bbf7)](https://app.codacy.com/gh/basher83/Zammad-MCP/dashboard)

An MCP server that connects AI assistants to Zammad, providing tools for managing tickets, users, organizations, and attachments.

> **Disclaimer**: This project is not affiliated with or endorsed by Zammad GmbH or the Zammad Foundation. This is an independent integration that uses the Zammad API.

## Features

### Tools

- **Ticket Management**
  - `zammad_search_tickets` - Search tickets with multiple filters
  - `zammad_get_ticket` - Get detailed ticket information with articles (supports pagination); custom object attributes are included
  - `zammad_create_ticket` - Create new tickets
  - `zammad_update_ticket` - Update ticket properties, including custom object attributes via `custom_fields`
  - `zammad_add_article` - Add comments/notes to tickets
  - `zammad_merge_tickets` - Merge a ticket into another (irreversible)
  - `zammad_add_ticket_tag` / `zammad_remove_ticket_tag` - Manage ticket tags
  - `zammad_bulk_update_tickets` - Update, assign, tag, or close up to 100 tickets in one call with per-ticket failure reporting
  - `zammad_get_ticket_tags` - Get tags assigned to a specific ticket
  - `zammad_list_tags` - List all tags defined in the system (requires admin.tag permission)
  - `zammad_export_tickets` - Export tickets with their conversation articles to a JSONL file on the server host (requires `ZAMMAD_EXPORT_DIR`; see [Ticket Export](#ticket-export-optional))

- **Attachment Support**
  - `zammad_get_article_attachments` - List attachments for a ticket article
  - `zammad_download_attachment` - Download attachment content (base64-encoded)

- **User & Organization Management**
  - `zammad_create_user` - Create a Zammad user
  - `zammad_get_user` / `zammad_search_users` - User information and search
  - `zammad_get_organization` / `zammad_search_organizations` - Organization data
  - `zammad_get_current_user` - Get authenticated user info

- **System Information**
  - `zammad_list_groups` - Get all available groups (cached for performance)
  - `zammad_list_ticket_states` - Get all ticket states (cached for performance)
  - `zammad_list_ticket_priorities` - Get all priority levels (cached for performance)
  - `zammad_get_ticket_stats` - Get ticket statistics (optimized with pagination)

- **Webhook Events** (HTTP transport only)
  - `zammad_list_events` - Poll ticket events delivered by Zammad webhooks (see [Webhook Events](#webhook-events-http-transport-only))

### Resources

Access Zammad data directly:

- `zammad://ticket/{id}` - Individual ticket details
- `zammad://user/{id}` - User profile information
- `zammad://organization/{id}` - Organization details
- `zammad://queue/{group}` - Ticket queue for a group

### Prompts

Pre-configured prompts:

- `analyze_ticket` - Comprehensive ticket analysis
- `draft_response` - Generate ticket responses
- `escalation_summary` - Summarize escalated tickets

## Installation

### Option 1: Run Directly with uvx (Recommended)

Run without installation:

```bash
# Install uv if you haven't already
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Run directly from GitHub
uvx --from git+https://github.com/basher83/zammad-mcp.git mcp-zammad

# Or with environment variables
ZAMMAD_URL=https://your-instance.zammad.com/api/v1 \
ZAMMAD_HTTP_TOKEN=your-api-token \
uvx --from git+https://github.com/basher83/zammad-mcp.git mcp-zammad
```

### Option 2: Docker Run

For production or containerized deployments:

```bash
# Basic usage with environment variables
docker run --rm -i \
  -e ZAMMAD_URL=https://your-instance.zammad.com/api/v1 \
  -e ZAMMAD_HTTP_TOKEN=your-api-token \
  ghcr.io/basher83/zammad-mcp:latest

# If you must skip TLS verification (self-signed / internal CA), add:
#   -e ZAMMAD_INSECURE=true

# Using Docker secrets for better security
docker run --rm -i \
  -e ZAMMAD_URL=https://your-instance.zammad.com/api/v1 \
  -e ZAMMAD_HTTP_TOKEN_FILE=/run/secrets/token \
  -v ./secrets/zammad_http_token.txt:/run/secrets/token:ro \
  ghcr.io/basher83/zammad-mcp:latest

# With .env file
docker run --rm -i \
  --env-file .env \
  ghcr.io/basher83/zammad-mcp:latest
```

#### Docker Image Versioning

The project publishes Docker images with semantic versioning:

- `latest` - Latest successful build from the default branch; may be unstable
- `1.2.3` - Specific version (recommended for production)
- `1.2` - Latest patch of 1.2 minor release
- `1` - Latest minor/patch of 1.x major release
- `main` - Latest main branch (may be unstable)

```bash
# Recommended for production - pin to specific version
docker pull ghcr.io/basher83/zammad-mcp:1.0.0
```

View all versions on [GitHub Container Registry](https://github.com/basher83/Zammad-MCP/pkgs/container/zammad-mcp).

### Option 3: For Developers

To contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/basher83/zammad-mcp.git
cd zammad-mcp

# Run the setup script
# On macOS/Linux:
./scripts/setup.sh

# On Windows (PowerShell):
.\scripts\setup.ps1
```

For manual setup, see the [Development](#development) section below.

## Configuration

The server requires a Zammad instance URL and an authentication method. Use a `.env` file:

1. Copy the example configuration:

   ```bash
   cp .env.example .env
   ```

1. Edit `.env` with your Zammad credentials:

   ```env
   # Required: Zammad instance URL (include /api/v1)
   ZAMMAD_URL=https://your-instance.zammad.com/api/v1

   # Authentication (choose one method):

   # Option 1: OAuth via Zammad's Doorkeeper (recommended for multi-user)
   # Users authenticate through Zammad's login page (which may offer
   # Google, GitHub, etc. depending on Zammad config). No static creds needed.
   # See "Auth Provider Configuration" section below.

   # Option 2: API Token (recommended for single-user / service accounts)
   ZAMMAD_HTTP_TOKEN=your-api-token

   # Option 3: OAuth2 Token (static)
   # ZAMMAD_OAUTH2_TOKEN=your-oauth2-token

   # Option 4: Username/Password
   # ZAMMAD_USERNAME=your-username
   # ZAMMAD_PASSWORD=your-password

   # Optional: Disable TLS certificate verification (NOT recommended for production)
   # Truthy values only: 1, true, yes, on. Unset (default) keeps TLS verification enabled.
   # ZAMMAD_INSECURE=true

   # Optional: Logging level (default: INFO)
   # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
   # LOG_LEVEL=INFO

   # Optional: Audit logging (see "Audit Logging" below)
   # ZAMMAD_AUDIT_LOG_ENABLED=true
   # ZAMMAD_AUDIT_LOG_DESTINATION=stderr  # stderr (default), file, or syslog
   # ZAMMAD_AUDIT_LOG_FILE=/var/log/mcp-zammad/audit.jsonl  # required for file
   # Optional: Resilience (see "Rate Limiting" under Troubleshooting)
   # ZAMMAD_RATE_LIMIT_ENABLED=false
   # ZAMMAD_RATE_LIMIT_REQUESTS=60
   # ZAMMAD_RATE_LIMIT_WINDOW=60
   # ZAMMAD_MAX_RETRIES=3
   # ZAMMAD_RETRY_BACKOFF_BASE=1.0
   # ZAMMAD_CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
   # ZAMMAD_CIRCUIT_BREAKER_RECOVERY_TIMEOUT=30

   # Optional: Transport Configuration
   # MCP_TRANSPORT=stdio  # Transport type: stdio (default) or http
   # MCP_HOST=127.0.0.1   # Host address for HTTP transport
   # MCP_PORT=8000        # Port number for HTTP transport
   ```

1. The server will automatically load the `.env` file on startup.

### Auth Provider Configuration (Optional)

Enable OAuth authentication so MCP clients authenticate through Zammad on the fly instead of relying on static credentials. Users log in with the exact same credentials and sign-in flow they already use to access Zammad's web UI — no separate API tokens or passwords to manage.

The MCP server proxies the OAuth flow to Zammad's built-in OAuth2 authorization server ([Doorkeeper](https://github.com/doorkeeper-gem/doorkeeper)). Zammad's login page may offer third-party sign-in options (Google, GitHub, etc.) depending on how the Zammad admin has configured the instance — that is entirely controlled by Zammad, not by this MCP server. The resulting Zammad bearer token is forwarded to the API so each user acts under their own identity.

When auth is configured, static Zammad credentials (`ZAMMAD_HTTP_TOKEN`, etc.) are not required.

#### Setup

Before configuring the environment variables below, you need to register this MCP server as an OAuth application in your Zammad instance. An OAuth application gives Zammad a way to identify the MCP server and allows it to issue access tokens on behalf of users who authorize the connection. This requires a Zammad admin API token.

1. **Create an OAuth application** in Zammad via the admin API:

   ```bash
   curl -X POST -H "Authorization: Token token=YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "MCP Server", "redirect_uri": "https://localhost:8000/auth/callback", "scopes": "full"}' \
     https://your-instance.zammad.com/api/v1/applications
   ```

   The `redirect_uri` must point to **this MCP server's** callback endpoint
   (`<MCP_AUTH_BASE_URL>/auth/callback`). For local development, use
   `https://localhost:8000/auth/callback` with a self-signed certificate
   (see [Transport Configuration](#transport-configuration-optional) below). In production, use the public URL where
   the MCP server is deployed (e.g. `https://mcp.yourdomain.com/auth/callback`).

   > **Important**: The `"scopes": "full"` field is required. Zammad's Doorkeeper
   > only supports the `full` scope — if the application is created without it,
   > MCP clients will receive an `invalid_scope` error during the OAuth flow.
   >
   > **Note**: Zammad enforces HTTPS redirect URIs in production mode.

2. **Retrieve the client ID and secret** (the standard API response hides them):

   ```bash
   curl -H "Authorization: Token token=YOUR_ADMIN_TOKEN" \
     "https://your-instance.zammad.com/api/v1/applications?full=true"
   ```

   The `uid` field is the client ID; the `secret` field is the client secret.

3. **Use HTTP transport** (`MCP_TRANSPORT=http`) — OAuth requires HTTP, not stdio.
   See [Transport Configuration](#transport-configuration-optional) below.

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_AUTH_CLIENT_ID` | - | OAuth client ID of this MCP server (`uid` from the Zammad OAuth application, see [Setup](#setup) above) |
| `MCP_AUTH_CLIENT_SECRET` | - | OAuth client secret of this MCP server (`secret` from the Zammad OAuth application, see [Setup](#setup) above) |
| `MCP_AUTH_BASE_URL` | - | Public URL of this MCP server (must use HTTPS if Zammad enforces it) |

The OAuth endpoints (`/oauth/authorize`, `/oauth/token`) are derived from `ZAMMAD_URL` automatically.

**Example:**

```env
MCP_AUTH_CLIENT_ID=your-zammad-oauth-app-uid
MCP_AUTH_CLIENT_SECRET=your-zammad-oauth-app-secret
MCP_AUTH_BASE_URL=https://localhost:8000
```

See [With Claude Desktop (HTTP + OAuth)](#with-claude-desktop-http--oauth) for Claude Desktop client configuration.

### Transport Configuration (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Transport type: `stdio` or `http` |
| `MCP_HOST` | `127.0.0.1` | Host address for HTTP transport |
| `MCP_PORT` | `8000` | Port number for HTTP transport |
| `MCP_SSL_CERTFILE` | - | Path to SSL certificate file (enables HTTPS) |
| `MCP_SSL_KEYFILE` | - | Path to SSL private key file |

### Audit Logging (Optional)

Audit logging is disabled by default. When enabled, the server writes one JSON object per line
(JSON Lines) for every MCP tool call, each Zammad connection attempt at startup, and each URL
security check that flags a local or private-network Zammad host.

| Variable | Default | Description |
|----------|---------|-------------|
| `ZAMMAD_AUDIT_LOG_ENABLED` | unset | Enable with `1`, `true`, `yes`, or `on` |
| `ZAMMAD_AUDIT_LOG_DESTINATION` | `stderr` | `stderr`, `file`, or `syslog` |
| `ZAMMAD_AUDIT_LOG_FILE` | - | Append target, required if destination is `file` |

Example record:

```json
{"timestamp": "2026-09-08T12:00:00+00:00", "event_type": "tool_call", "action": "zammad_get_ticket", "success": true, "duration_ms": 12.5, "details": {}}
```

Event types are `tool_call`, `authentication`, and `security_validation`. Records never contain
tool arguments, Zammad responses, credentials, or full URLs; failures are recorded by exception
type only, and any `details` key containing `password`, `token`, `secret`, `authorization`,
`credential`, or `data` is redacted. Audit output never uses stdout, so the default `stderr`
destination is safe for the stdio transport. Invalid enabled configuration (unknown destination or
missing file path) fails at startup.

### Ticket Export (Optional)

`zammad_export_tickets` is read-only against Zammad but writes a JSON Lines file on the host running
the MCP server: one JSON object per ticket, with its title, group, state, priority, timestamps,
optional tags, and conversation articles converted to plain text. It is intended for bulk exports
that would exceed MCP response-size limits. Without filters it pages through the list endpoint (no
result cap); with `query`, `group`, `state`, `created_after`, or `created_before` it uses the search
endpoint, which Zammad caps at 10,000 results. Internal articles are excluded unless
`include_internal_articles` is set, and tags cost one extra request per ticket when `include_tags`
is set.

| Variable | Default | Description |
|----------|---------|-------------|
| `ZAMMAD_EXPORT_DIR` | unset | Directory exports are confined to. Export is disabled until it is set to an existing directory |

Filesystem confinement: `output_path` must end in `.jsonl`. Relative paths are resolved inside
`ZAMMAD_EXPORT_DIR`; absolute paths are accepted only if they resolve inside it. Symlinks are
resolved before the containment check, so `..` traversal or a symlink pointing outside the directory
is rejected. The file is opened in append mode and flushed per ticket, so an interrupted export can
be continued with `resume_from_page`. Per-ticket failures are counted and reported in the summary
without stopping the export.

**Important**: Keep your `.env` file out of version control (already in `.gitignore`).

## Response Formats

All data-returning tools support two output formats:

- **Markdown** (default): Human-readable format optimized for LLM consumption
- **JSON**: Machine-readable format with complete metadata

Example:

```python
# Markdown (default)
zammad_search_tickets(query="network", response_format="markdown")

# JSON
zammad_search_tickets(query="network", response_format="json")
```

## Usage

### With Claude Desktop (stdio)

The simplest setup uses stdio transport with a static API token. Claude Desktop
launches the server as a subprocess — no network configuration needed.

**Using uvx (no installation required):**

```json
{
  "mcpServers": {
    "zammad": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/basher83/zammad-mcp.git", "mcp-zammad"],
      "env": {
        "ZAMMAD_URL": "https://your-instance.zammad.com/api/v1",
        "ZAMMAD_HTTP_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Using Docker:**

```json
{
  "mcpServers": {
    "zammad": {
      "command": "docker",
      "args": ["run", "--rm", "-i",
               "-e", "ZAMMAD_URL=https://your-instance.zammad.com/api/v1",
               "-e", "ZAMMAD_HTTP_TOKEN=your-api-token",
               "ghcr.io/basher83/zammad-mcp:latest"]
    }
  }
}
```

> **Important**: The `-i` flag is required — without it, the MCP server cannot
> receive stdin. Preserve this flag in wrapper scripts or shell aliases.

**Using a local clone:**

```json
{
  "mcpServers": {
    "zammad": {
      "command": "python",
      "args": ["-m", "mcp_zammad"],
      "env": {
        "ZAMMAD_URL": "https://your-instance.zammad.com/api/v1",
        "ZAMMAD_HTTP_TOKEN": "your-api-token"
      }
    }
  }
}
```

### With Claude Desktop (HTTP + OAuth)

When using [OAuth authentication](#auth-provider-configuration-optional), the server
uses HTTP transport and must be started as a separate process (see
[HTTP Transport (Remote/Cloud Deployment)](#http-transport-remotecloud-deployment) — unlike stdio, where
Claude Desktop launches it automatically). Claude Desktop connects to the running
server via [mcp-remote](https://www.npmjs.com/package/mcp-remote), which bridges
its stdio interface to the MCP server's HTTP endpoint and handles the OAuth flow.

#### Local development setup

For local development, the MCP server needs HTTPS because Zammad enforces HTTPS
redirect URIs. Generate a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost"
```

Configure the SSL paths in your `.env`:

```env
MCP_SSL_CERTFILE=cert.pem
MCP_SSL_KEYFILE=key.pem
```

Start the server:

```bash
uv run python -m mcp_zammad
```

> **Note**: The `.env` file in the current directory is loaded automatically.

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "zammad": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://localhost:8000/mcp"],
      "env": {
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}
```

> **Note**: `NODE_TLS_REJECT_UNAUTHORIZED=0` tells Node.js to accept the self-signed
> certificate. This is only needed for local development — do not use in production.

On first connection, `mcp-remote` opens your browser to Zammad's login page.
After authenticating, your Zammad identity is used automatically for all API calls.

#### Production setup

In production, the MCP server is deployed with a proper TLS certificate — typically
behind a reverse proxy (see [HTTP Transport (Remote/Cloud Deployment)](#http-transport-remotecloud-deployment)).
No self-signed certificates or `NODE_TLS_REJECT_UNAUTHORIZED` needed.

**Claude Desktop via `mcp-remote`:**

```json
{
  "mcpServers": {
    "zammad": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://mcp.yourdomain.com/mcp"]
    }
  }
}
```

**MCP clients with native HTTP transport support (no `mcp-remote` needed):**

```json
{
  "mcpServers": {
    "zammad": {
      "url": "https://mcp.yourdomain.com/mcp"
    }
  }
}
```

### Standalone Usage (stdio)

```bash
# Run the server (reads .env from current directory)
uv run python -m mcp_zammad

# Or with explicit environment variables
ZAMMAD_URL=https://your-instance.zammad.com/api/v1 \
ZAMMAD_HTTP_TOKEN=your-api-token \
python -m mcp_zammad
```

### HTTP Transport (Remote/Cloud Deployment)

#### Running the server

The server's transport and authentication are configured via environment variables
or a `.env` file (see [Transport Configuration](#transport-configuration-optional)
and [Auth Provider Configuration](#auth-provider-configuration-optional)).

**Direct Python:**

```bash
# With OAuth (recommended for multi-user)
MCP_TRANSPORT=http \
MCP_PORT=8000 \
uvx --from git+https://github.com/basher83/zammad-mcp.git mcp-zammad

# With static credentials (single-user)
MCP_TRANSPORT=http \
MCP_PORT=8000 \
ZAMMAD_URL=https://your-instance.zammad.com/api/v1 \
ZAMMAD_HTTP_TOKEN=your-api-token \
uvx --from git+https://github.com/basher83/zammad-mcp.git mcp-zammad
```

**Docker:**

```bash
docker run -d \
  --name zammad-mcp \
  -p 8000:8000 \
  --env-file .env \
  ghcr.io/basher83/zammad-mcp:latest
```

Access the MCP endpoint at `http://localhost:8000/mcp`.

#### Production Deployment with Reverse Proxy

⚠️ **SECURITY WARNING**: Unless [OAuth authentication](#auth-provider-configuration-optional) is enabled, the server
does not authenticate inbound MCP clients. `ZAMMAD_*` credentials authenticate the server to Zammad; they do not
authenticate MCP clients. Without OAuth, bind to `0.0.0.0` only behind an authenticated TLS proxy or inside a network
restricted to trusted clients.

Use a reverse proxy for TLS and client authentication. The Caddy example below provides TLS only; add an
authentication policy appropriate for your environment before exposing it outside a trusted network.

**Example with Caddy:**

```bash
# Start the MCP server behind a reverse proxy
MCP_TRANSPORT=http \
MCP_HOST=0.0.0.0 \
MCP_PORT=8000 \
uvx --from git+https://github.com/basher83/zammad-mcp.git mcp-zammad
```

**Caddyfile example:**

```caddy
mcp.yourdomain.com {
    reverse_proxy localhost:8000
    # Caddy automatically handles HTTPS/TLS
}
```

**Production checklist:**

1. Use `MCP_HOST=0.0.0.0` only behind a reverse proxy
2. Enable HTTPS/TLS via reverse proxy (or `MCP_SSL_CERTFILE`/`MCP_SSL_KEYFILE`)
3. Enable [OAuth authentication](#auth-provider-configuration-optional) for per-user access control
4. Restrict access with firewall rules

#### Client Configuration for HTTP

Configure your MCP client to use HTTP transport:

```json
{
  "mcpServers": {
    "zammad": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Security Considerations

1. **Local development**: Use `MCP_HOST=127.0.0.1` (localhost only)
2. **Production**: Enable [OAuth authentication](#auth-provider-configuration-optional) for per-user identity
3. **HTTPS**: Use a reverse proxy for TLS, or the built-in SSL support
4. **Firewall**: Restrict access to trusted networks
5. **Host/Origin Validation**: Configure this at the authenticated proxy; the server does not add it automatically

### Webhook Events (HTTP Transport Only)

Instead of repeatedly searching for changed tickets, Zammad can push ticket events to the server, and MCP clients poll
them with `zammad_list_events`. This needs `MCP_TRANSPORT=http`; stdio mode has no inbound listener.

1. **Configure a secret** (the endpoint answers `503` until it is set):

   ```bash
   export ZAMMAD_WEBHOOK_SECRET="$(openssl rand -hex 32)"
   ```

2. **Expose `POST /webhooks/zammad`** to your Zammad instance, behind TLS (reverse proxy). The signature proves the
   payload came from Zammad but does not encrypt it.

3. **Create the webhook in Zammad** (admin only): *Manage → Webhooks → New Webhook*
   - Endpoint: `https://your-mcp-host/webhooks/zammad`
   - HMAC SHA1 Signature Token: the same value as `ZAMMAD_WEBHOOK_SECRET`
   - Keep the default JSON payload (the server reads `ticket.id`, `ticket.number`, `ticket.article_count`,
     `ticket.updated_at`, and `article.id`)

4. **Create a trigger** (*Manage → Triggers → New Trigger*) that fires on the ticket actions you care about and executes
   the webhook.

The server maps deliveries to `ticket.create` (first article), `ticket.article.create` (later articles), or
`ticket.update` (no article in payload). Invalid or missing `X-Hub-Signature` headers return `401`; non-ticket or
malformed payloads return `400`. Only identifiers and timestamps are retained — never article bodies.

Retention is process-local and bounded (1000 events, oldest evicted first) and is lost on restart. Poll with
`zammad_list_events`, which returns the oldest events after `since` first (up to `limit`); pass the returned
`next_since` as `since` on the next call and repeat until `events` is empty, then fetch details with
`zammad_get_ticket`.

## Examples

### Search for Open Tickets

```plaintext
Use zammad_search_tickets with state="open" to find all open tickets
```

### Create a Support Ticket

```plaintext
Use zammad_create_ticket with:
- title: "Customer needs help with login"
- group: "Support"
- customer: "customer@example.com"
- article_body: "Customer reported unable to login..."
```

### Update and Respond to a Ticket

```plaintext
1. Use zammad_get_ticket with ticket_id=123 to see the full conversation
2. Use zammad_add_article to add your response
3. Use zammad_update_ticket to change state to "pending reminder" with a pending_time (e.g. "2026-07-01T08:00:00Z")
```

### Analyze Escalated Tickets

```plaintext
Use the escalation_summary prompt to get a report of all tickets approaching escalation
```

### Upload Attachments to a Ticket

```plaintext
Use zammad_add_article with attachments parameter:
- ticket_id: 123
- body: "See attached documentation"
- attachments: [
    {
      "filename": "guide.pdf",
      "data": "JVBERi0xLjQKJ...",  # base64-encoded content
      "mime_type": "application/pdf"
    }
  ]
```

### Merge Duplicate Tickets

Useful for collapsing recurring auto-generated tickets (cron failures, monitoring noise) into one incident. The source ticket's articles move to the target and the source is closed as "merged". This cannot be undone.

```plaintext
Use zammad_merge_tickets with:
- source_ticket_id: 123          # internal ID of the ticket to merge away
- target_ticket_number: "20002"  # display number of the surviving ticket
```

`target_ticket_id` may be given instead of `target_ticket_number`, but not both.

## Development

### Setup

#### Using Setup Scripts (Recommended)

```bash
# Clone the repository
git clone https://github.com/basher83/zammad-mcp.git
cd zammad-mcp

# Run the setup script
# On macOS/Linux:
./scripts/setup.sh

# On Windows (PowerShell):
.\scripts\setup.ps1
```

#### Manual Setup

```bash
# Clone the repository
git clone https://github.com/basher83/zammad-mcp.git
cd zammad-mcp

# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
```

### Project Structure

```plaintext
zammad-mcp/
├── mcp_zammad/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py      # MCP server implementation
│   ├── client.py      # Zammad API client wrapper
│   ├── config.py      # Transport and OAuth configuration
│   └── models.py      # Pydantic models
├── tests/
├── scripts/
│   └── uv/            # UV single-file scripts
├── pyproject.toml
├── README.md
├── Dockerfile
└── .env.example
```

### Running Tests

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_zammad
```

### Code Quality

```bash
# Format code
uv run ruff format mcp_zammad tests

# Lint
uv run ruff check mcp_zammad tests

# Type checking
uv run mypy mcp_zammad

# Run all quality checks
./scripts/quality-check.sh
```

## API Token Generation

To generate an API token in Zammad:

1. Log into your Zammad instance
1. Click on your avatar → Profile
1. Navigate to "Token Access"
1. Click "Create"
1. Name your token (e.g., "MCP Server")
1. Select appropriate permissions
1. Copy the generated token

## Troubleshooting

### Connection Issues

- Verify your Zammad URL includes the protocol (https://)
- Check that your API token has the necessary permissions
- Ensure your Zammad instance is accessible from your network
- For self-signed/internal certs only: set `ZAMMAD_INSECURE=true` to bypass TLS verification

### Authentication Errors

- Use API tokens over username/password
- Ensure tokens have permissions for the operations
- Check token expiration in Zammad settings

### Rate Limiting

The client wraps every Zammad request with retries, an optional client-side throttle, and a circuit breaker.

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZAMMAD_RATE_LIMIT_ENABLED` | `false` | Opt in to client-side throttling |
| `ZAMMAD_RATE_LIMIT_REQUESTS` | `60` | Max requests per window (>= 1) |
| `ZAMMAD_RATE_LIMIT_WINDOW` | `60` | Window length in seconds (> 0) |
| `ZAMMAD_MAX_RETRIES` | `3` | Retries for safe reads; `0` disables |
| `ZAMMAD_RETRY_BACKOFF_BASE` | `1.0` | Backoff seconds: `base * 2^attempt` |
| `ZAMMAD_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | `5` | Consecutive failures before failing fast |
| `ZAMMAD_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` | `30` | Seconds before requests are allowed again; one more failure re-opens the circuit |

Behavior to be aware of:

- Only `GET`/`HEAD`/`OPTIONS` are retried, on HTTP 429/500/502/503/504, connection errors, and timeouts.
  Writes (`POST`/`PUT`/`PATCH`/`DELETE`) are sent exactly once so a slow Zammad never duplicates a ticket or article.
- A `Retry-After` header expressed in seconds overrides the backoff (capped at 60s); other formats fall back to backoff.
- Throttling and circuit state are per process. Multiple server instances do not share a budget.
- When retries are exhausted or the circuit is open, tools return an `Error:` message naming the cause: a 429
  outcome (or a throttled write) points at rate limiting and `ZAMMAD_RATE_LIMIT_ENABLED`; a 5xx outcome reports a
  server error. Reduce request frequency, paginate, or enable throttling if you keep hitting Zammad's limits.

## Security

The server implements multiple layers of protection following industry best practices.

### Reporting Security Issues

**⚠️ IMPORTANT**: Do not create public GitHub issues for security vulnerabilities.

Report via [GitHub Security Advisories](https://github.com/basher83/Zammad-MCP/security/advisories/new) (preferred) or see [SECURITY.md](SECURITY.md).

### Security Features

- ✅ **Request Validation**: Strict request models reject unknown fields and validate constrained inputs ([models.py](mcp_zammad/models.py))
- ⚠️ **URL Validation**: Rejects malformed and non-HTTP(S) URLs, but does not block private-network targets ([client.py](mcp_zammad/client.py))
- ✅ **HTML Sanitization**: Sanitizes selected HTML-bearing fields ([models.py](mcp_zammad/models.py))
- ✅ **Upstream Authentication**: Supports API tokens, OAuth2, and username/password for Zammad ([client.py](mcp_zammad/client.py))
- ✅ **Audit Logging**: Opt-in JSON Lines records for tool calls, connection outcomes, and URL checks with secret redaction ([audit.py](mcp_zammad/audit.py))
- ✅ **OAuth Authentication**: Per-user inbound authentication via Zammad's Doorkeeper OAuth2 provider ([config.py](mcp_zammad/config.py))
- ✅ **Dependency Scanning**: CI runs pip-audit; Dependabot security alerts are enabled separately in GitHub
- ✅ **Security Testing**: CI runs Bandit and pip-audit ([security-scan.yml](.github/workflows/security-scan.yml))

See [SECURITY.md](SECURITY.md) for complete documentation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code standards, testing, and pull request guidelines.

## License

[AGPL-3.0-or-later](LICENSE) — matches the [Zammad project](https://github.com/zammad/zammad) license.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical design
- [SECURITY.md](SECURITY.md) — Security policy
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development guidelines
- [CHANGELOG.md](CHANGELOG.md) — Version history

## Support

- [GitHub Issues](https://github.com/basher83/Zammad-MCP/issues)
- [Zammad Documentation](https://docs.zammad.org/)
- [MCP Documentation](https://modelcontextprotocol.io/)

## Trademark Notice

"Zammad" is a trademark of Zammad GmbH. This independent integration is not affiliated with or endorsed by Zammad GmbH or the Zammad Foundation. The name "Zammad" indicates compatibility with the Zammad ticket system.
