#### Step 4: Ensure User Permissions

Make sure your OTRS user has appropriate permissions for:

- Creating and updating tickets
- Accessing configuration items
- Using the Generic Interface

## Usage

### Docker (Recommended)

The easiest way to run otrs-mcp with [Claude Desktop](https://claude.ai/desktop) is using Docker. If you don't have Docker installed, you can get it from [Docker's official website](https://www.docker.com/get-started/).

Edit your Claude Desktop config file:

- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Then add the following configuration:

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
        "your-registry/otrs-mcp"
      ]
    }
  }
}
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

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
