# OTRS MCP Server

A [Model Context Protocol][mcp] (MCP) server for OTRS (Open Ticket Request System) API integration.

This provides access to OTRS ticket management, configuration items, and other OTRS functionality through standardized MCP interfaces, allowing AI assistants to create, search, and manage tickets and configuration items.

[mcp]: https://modelcontextprotocol.io/introduction/introduction

## Features

- [x] Create, read, update, and search tickets
- [x] Access ticket history and detailed information
- [x] Manage configuration items (CMDB)
- [x] Session management and authentication
- [x] Configurable default values for tickets
- [x] Docker containerization support
- [x] SSL/TLS support with certificate verification options
- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.

## Prerequisites

### OTRS Server Configuration

Before using this MCP server, you need to configure your OTRS instance:

#### Step 1: Access OTRS Admin Panel

- URL: `https://your-otrs-server/otrs/index.pl?Action=Admin`
- Login with your admin credentials

#### Step 2: Configure Web Services

1. Navigate to: **System Administration → Web Services**
2. Create or verify you have a webservice (e.g., "TestInterface") with these operations:
   - ✅ SessionCreate
   - ✅ TicketCreate
   - ✅ TicketGet
   - ✅ TicketSearch
   - ✅ TicketUpdate
   - ✅ TicketHistoryGet
   - ✅ ConfigItemGet
   - ✅ ConfigItemSearch

#### Step 3: Note Your Webservice URL

Your webservice URL should look like:

`https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/YourWebserviceName`

#### Step 4: Ensure User Permissions

Make sure your OTRS user has appropriate permissions for:

- Creating and updating tickets
- Accessing configuration items
- Using the Generic Interface

## Usage

### Docker (Recommended)

The easiest way to run otrs-mcp with [Claude Desktop](https://claude.ai/desktop) is using Docker. If you don't have Docker installed, you can get it from [Docker's official website](https://www.docker.com/get-started/).

#### Using Pre-built Image

You can use the pre-built Docker image from GitHub Container Registry:

```json
{
  "mcpServers": {
    "otrs": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "OTRS_BASE_URL=https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface",
        "-e",
        "OTRS_USERNAME=your-username",
        "-e",
        "OTRS_PASSWORD=your-password",
        "-e",
        "OTRS_VERIFY_SSL=false",
        "-e",
        "OTRS_DEFAULT_QUEUE=Raw",
        "-e",
        "OTRS_DEFAULT_STATE=new",
        "-e",
        "OTRS_DEFAULT_PRIORITY=3 normal",
        "ghcr.io/yourusername/otrs-mcp-server:latest"
      ]
    }
  }
}
```

#### Building Locally

If you prefer to build the image locally:

```bash
# Clone the repository
git clone https://github.com/yourusername/otrs-mcp-server.git
cd otrs-mcp-server

# Build the Docker image
docker build -t otrs-mcp-server .

# Run the container
docker run --rm -i \
  -e OTRS_BASE_URL="https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface" \
  -e OTRS_USERNAME="your-username" \
  -e OTRS_PASSWORD="your-password" \
  -e OTRS_VERIFY_SSL="false" \
  otrs-mcp-server
```

### Running with UV

Alternatively, you can run the server directly using UV. First, set your environment variables:

```bash
export OTRS_BASE_URL="https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface"
export OTRS_USERNAME="your-username"
export OTRS_PASSWORD="your-password"
export OTRS_VERIFY_SSL="false"
export OTRS_DEFAULT_QUEUE="Raw"
export OTRS_DEFAULT_STATE="new"
export OTRS_DEFAULT_PRIORITY="3 normal"
export OTRS_DEFAULT_TYPE="Unclassified"
```

Then edit your Claude Desktop config file and add the server configuration:

```json
{
  "mcpServers": {
    "otrs": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to otrs-mcp-server directory>",
        "run",
        "src/otrs_mcp/main.py"
      ],
      "env": {
        "OTRS_BASE_URL": "https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface",
        "OTRS_USERNAME": "your-username",
        "OTRS_PASSWORD": "your-password",
        "OTRS_VERIFY_SSL": "false"
      }
    }
  }
}
```

> Note: if you see `Error: spawn uv ENOENT` in [Claude Desktop](https://claude.ai/desktop), you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

## Environment Variables

| Variable                | Required | Default        | Description                         |
| ----------------------- | -------- | -------------- | ----------------------------------- |
| `OTRS_BASE_URL`         | ✅       | -              | Base URL for OTRS webservice        |
| `OTRS_USERNAME`         | ✅       | -              | OTRS username                       |
| `OTRS_PASSWORD`         | ✅       | -              | OTRS password                       |
| `OTRS_VERIFY_SSL`       | ❌       | `false`        | Enable SSL certificate verification |
| `OTRS_DEFAULT_QUEUE`    | ❌       | `Raw`          | Default queue for new tickets       |
| `OTRS_DEFAULT_STATE`    | ❌       | `new`          | Default state for new tickets       |
| `OTRS_DEFAULT_PRIORITY` | ❌       | `3 normal`     | Default priority for new tickets    |
| `OTRS_DEFAULT_TYPE`     | ❌       | `Unclassified` | Default type for new tickets        |

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

### Testing

Test your OTRS connection and API functionality:

```bash
# Set environment variables
export OTRS_BASE_URL="https://your-otrs-server/otrs/nph-genericinterface.pl/Webservice/TestInterface"
export OTRS_USERNAME="your-username"
export OTRS_PASSWORD="your-password"
export OTRS_VERIFY_SSL="false"

# Run connectivity test
uv run python tests/connectivity_test.py

# Run API functionality test
uv run python tests/test_working_api.py

# Run debug diagnostics
uv run python tests/debug_test.py
```

The project includes test scripts that help verify your OTRS configuration and API connectivity.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### Publishing Docker Image

To publish the Docker image to GitHub Container Registry for public use:

#### Prerequisites

1. **GitHub Account** with a repository for this project
2. **GitHub Personal Access Token** with `write:packages` permission
3. **Docker** installed locally

#### Step-by-Step Publishing

1. **Create GitHub Personal Access Token**:

   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `write:packages` and `read:packages` permissions
   - Save the token securely

2. **Login to GitHub Container Registry**:

   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
   ```

3. **Build and Tag the Image**:

   ```bash
   # Build the image
   docker build -t otrs-mcp-server .

   # Tag for GitHub Container Registry
   docker tag otrs-mcp-server ghcr.io/yourusername/otrs-mcp-server:latest
   docker tag otrs-mcp-server ghcr.io/yourusername/otrs-mcp-server:v0.1.0
   ```

4. **Push to Registry**:

   ```bash
   # Push latest tag
   docker push ghcr.io/yourusername/otrs-mcp-server:latest

   # Push version tag
   docker push ghcr.io/yourusername/otrs-mcp-server:v0.1.0
   ```

5. **Make Package Public** (Optional):
   - Go to your GitHub repository
   - Navigate to Packages section
   - Click on your package
   - Go to Package settings
   - Change visibility to Public

#### Automated Publishing with GitHub Actions

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

#### Alternative: Docker Hub

To publish to Docker Hub instead:

```bash
# Login to Docker Hub
docker login

# Tag for Docker Hub
docker tag otrs-mcp-server yourusername/otrs-mcp-server:latest
docker tag otrs-mcp-server yourusername/otrs-mcp-server:v0.1.0

# Push to Docker Hub
docker push yourusername/otrs-mcp-server:latest
docker push yourusername/otrs-mcp-server:v0.1.0
```

Then update the Claude Desktop config to use:

```json
"ghcr.io/yourusername/otrs-mcp-server:latest"
```

or

```json
"yourusername/otrs-mcp-server:latest"
```

## Available Tools

### 🎫 Ticket Management

- `create_ticket` - Create a new ticket in OTRS
- `get_ticket` - Get detailed information about a specific ticket
- `search_tickets` - Search for tickets based on various criteria
- `update_ticket` - Update an existing ticket's properties
- `get_ticket_history` - Get the complete history of a ticket

### 🔧 Configuration Items (CMDB)

- `get_config_item` - Get detailed information about a configuration item
- `search_config_items` - Search for configuration items

### 🔐 Session Management

- `create_session` - Create a new OTRS session for authentication

### 📊 Resources

- `otrs://ticket/{ticket_id}` - Direct access to ticket data
- `otrs://ticket/{ticket_id}/history` - Access to ticket history
- `otrs://search/tickets` - Overview of recent tickets
- `otrs://configitem/{config_item_id}` - Access to configuration item data

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**: Set `OTRS_VERIFY_SSL=false` for self-signed certificates
2. **HTTP 301 Redirects**: Ensure you're using HTTPS URLs if your OTRS server redirects HTTP to HTTPS
3. **Authentication Failures**: Verify your username, password, and webservice configuration
4. **Missing Operations**: Check that your OTRS webservice includes all required operations

### Debug Mode

Run the debug script to diagnose connection issues:

```bash
uv run python tests/debug_test.py
```

This will test both HTTP and HTTPS connections and provide detailed error information.

### Example Working Configuration

For reference, here's a working configuration example:

```bash
# Environment variables
export OTRS_BASE_URL="https://192.168.5.159/otrs/nph-genericinterface.pl/Webservice/TestInterface"
export OTRS_USERNAME="seasonpoon.admin"
export OTRS_PASSWORD="your-password"
export OTRS_VERIFY_SSL="false"
export OTRS_DEFAULT_QUEUE="Raw"
export OTRS_DEFAULT_STATE="new"
export OTRS_DEFAULT_PRIORITY="3 normal"
export OTRS_DEFAULT_TYPE="Unclassified"
```

### OTRS Webservice Operations

Your OTRS webservice should include these operations:

| Operation Name   | Controller                   | Description                    |
| ---------------- | ---------------------------- | ------------------------------ |
| SessionCreate    | Session::SessionCreate       | Create authentication sessions |
| TicketCreate     | Ticket::TicketCreate         | Create new tickets             |
| TicketGet        | Ticket::TicketGet            | Retrieve ticket details        |
| TicketSearch     | Ticket::TicketSearch         | Search for tickets             |
| TicketUpdate     | Ticket::TicketUpdate         | Update existing tickets        |
| TicketHistoryGet | Ticket::TicketHistoryGet     | Get ticket history             |
| ConfigItemGet    | ConfigItem::ConfigItemGet    | Retrieve configuration items   |
| ConfigItemSearch | ConfigItem::ConfigItemSearch | Search configuration items     |

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
