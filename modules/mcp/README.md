# HackerOne GraphQL MCP Server
Derailed slightly, since the mcp server in the dockerhub version doesn't work as is outside of docker
```
Usage: apollo-mcp-server.exe [OPTIONS] [APOLLO_REGISTRY_URL]

Arguments:
  [APOLLO_REGISTRY_URL]  [env: APOLLO_REGISTRY_URL=]

Options:
  -d, --directory <DIRECTORY>

   The working directory to use
  -s, --schema <SCHEMA>

   The path to the GraphQL API schema file
  -c, --custom-scalars-config <CUSTOM_SCALARS_CONFIG>
The path to the GraphQL custom_scalars_config file
  -e, --endpoint <ENDPOINT>

   The GraphQL endpoint the server will invoke [default: http://127.0.0.1:4000]

--header <HEADERS> Headers to send to the endpoint

--sse-address <SSE_ADDRESS>

   The IP address to bind the SSE server to

--sse-port <SSE_PORT>

   Start the server using the SSE transport on the given port
  -i, --introspection

   Expose the schema to the MCP client through `introspect` and `execute` tools
  -u, --uplink

   Enable use of uplink to get the schema and persisted queries (requires APOLLO_KEY and APOLLO_GRAPH_REF)
  -x, --explorer

   Expose a tool to open queries in Apollo Explorer (requires APOLLO_GRAPH_REF)
  -o, --operations [<OPERATIONS>...]

   Operation files to expose as MCP tools

--manifest <MANIFEST>

   The path to the persisted query manifest containing operations
  -m, --allow-mutations <ALLOW_MUTATIONS>

   [default: none] [possible values: none, explicit, all]

--disable-type-description

   Disable operation root field types in tool description

--disable-schema-description

   Disable schema type definitions referenced by all fields returned by the operation in the tool description
  -l, --log <LOG_LEVEL>

   The log level for the MCP Server [default: INFO]

--http-address <HTTP_ADDRESS>
   The IP address to bind the Streamable HTTP server to

--http-port <HTTP_PORT>

   Start the server using the Streamable HTTP transport on the given port

--collection <COLLECTION>

   collection id to expose as MCP tools (requires APOLLO_KEY)

--apollo-uplink-endpoints <APOLLO_UPLINK_ENDPOINTS>

   The endpoints (comma separated) polled to fetch the latest supergraph schema [env: APOLLO_UPLINK_ENDPOINTS=]

--apollo-key <APOLLO_KEY>

   Your Apollo key [env: APOLLO_KEY=]

--apollo-graph-ref <APOLLO_GRAPH_REF>

   Your Apollo graph reference [env: APOLLO_GRAPH_REF=]
  -h, --help

   Print help (see more with '--help')
(base) PS C:\Users\jbras\.lmstudio\bin> cd ..
(base) PS C:\Users\jbras\.lmstudio> .\bin\apollo-mcp-server.exe

```
A Docker image that provides access to HackerOne's GraphQL API through the Model Context Protocol (MCP).

**Supported MCP transport types**: Currently only stdio transport is supported. Please file an issue if you require [other transports](https://modelcontextprotocol.io/docs/concepts/transports#built-in-transport-types).

**Multi-Architecture Support**: This image supports both Intel/AMD (amd64) and Apple Silicon (arm64) architectures.

## Quick Start

1. **Run with an MCP client**:
   ```sh
   docker run -i --rm \
     -e ENDPOINT="https://hackerone.com/graphql" \
     -e TOKEN="<your_base64_encoded_token>" \
     -e ALLOW_MUTATIONS="none" \
     hackertwo/hackerone-graphql-mcp-server:latest
   ```

## Docker Image Tags

- **`latest`**: Latest stable release (only updated on version releases)
- **`dev-main`**: Development builds from main branch
- **`1.x.x`**: Specific version releases
- **`pr-<ref>`**: Pull request builds

## Environment Variables

- `ENDPOINT`: GraphQL endpoint URL (default: https://hackerone.com/graphql)
- `TOKEN`: Base64 encoded API token in format: `base64(username:api_key)`
- `ALLOW_MUTATIONS`: Controls which mutations are allowed (default: none)
  - `none`: No mutations allowed
  - `explicit`: Only explicitly defined mutations allowed
  - `all`: All mutations allowed

## Generating an API Token

1. Visit https://hackerone.com/settings/api_token/edit to generate an API key
2. Encode as: `echo -n "username:api_key" | base64`
3. Use the resulting string as your TOKEN value

## Example config in editor (Zed)
```json
{
  "context_servers": {
    "hackerone-graphql-mcp-server": {
      "command": {
        "path": "/usr/local/bin/docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "-e",
          "ENDPOINT=https://hackerone.com/graphql",
          "-e",
          "TOKEN=<your_base64_encoded_token>",
          "-e",
          "ALLOW_MUTATIONS=none",
          "hackertwo/hackerone-graphql-mcp-server:latest"
        ]
      },
      "settings": {}
    }
  }
}
```

## Notes

- The Docker container is designed to be piped into an MCP-compatible client
- Running the container directly will result in an error as it expects an MCP client connection
- The `-i` flag is required to maintain standard input for the stdio transport
- The `schema.graphql` in this repository may become outdated over time, you can download the latest one from HackerOne at [https://hackerone.com/schema.graphql](https://hackerone.com/schema.graphql)

## Development

### Creating a Release

To create a new release:

1. Create a [new release in GitHub](https://github.com/Hacker0x01/hackerone-graphql-mcp-server/releases/new).

2. GitHub Actions will automatically:
   - Build multi-architecture images (amd64, arm64)
   - Push to Docker Hub with appropriate tags
   - Update the `latest` tag

### Manual Build (Local Development)

For local development and testing:

```sh
# Setup buildx
docker buildx create --name multiarch --driver docker-container --use
docker buildx inspect --bootstrap

# Build and push the image
bin/build

# Clean up
docker buildx rm multiarch
```

### Updating the GraphQL schema

```sh
curl https://hackerone.com/schema.graphql -o graphql/schema.graphql
```
