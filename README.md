# Simple API Mock Server

A simple, file-based API mocking server built with Flask, designed to help developers quickly simulate API endpoints for testing and development.

## 🔧 Features

### Core Functionality

- **Dynamic Routing:** Define API endpoints from a `api.json` or `api.yaml` file.
- **OpenAPI Specification:** Automatically generates a rich OpenAPI v3 specification at `/openapi.json`.
- **Metrics Endpoint:** Exposes Prometheus-style metrics at `/metrics`.
- **Graceful 404 Handling:** Custom JSON 404 responses for unknown routes.
- **CORS Support:** Integrated `Flask-Cors` to handle Cross-Origin Resource Sharing.

### Configuration & Customization

- **YAML Configuration:** Supports `.yml` and `.yaml` configuration files.
- **Templating for Request Body Parameters:** Responses can be dynamically templated using values from the request body.
- **Custom Response Headers per Method:** Define specific HTTP headers for different methods within the same route.
- **Descriptions and Metadata:** Add optional `description` and `tags` fields to your API endpoints for better documentation and categorization.
- **Example Request Bodies:** Include optional `request_body` fields in `api.json` for documenting expected request payloads.
- **Static File Serving:** Serve static files (e.g., UI assets) from a specified folder via a CLI argument.

### Authentication & Security

- **Improved Authentication Logic:** Refactored for clarity, consistency, and maintainability.
- **Granular Rate Limiting:** Rate limiting can now be applied per client IP or API key for more realistic throttling. Old rate limit entries are pruned to prevent memory growth.
- **API Key in Query Params:** API keys can be sent via query parameters (`?api_key=...`) as well as headers.
- **Auth Challenge Headers:** 401 Unauthorized responses for Basic and Bearer auth now include `WWW-Authenticate` headers.

### Development & Operations

- **Enhanced Metrics Tracking:** Thread-safe and semantically clearer metrics using `collections.Counter`.
- **Robust Error Handling:** Improved error logging with `logger.exception()` and user-friendly messages for port binding errors and malformed JSON.
- **Thread-Safe Rate Limiting:** Implemented `threading.Lock` to prevent race conditions in rate limiting.
- **Hot Reloading:** Automatically restarts the server when `api.json` changes (requires `--debug` flag).
- **Graceful Shutdown:** Handles `SIGINT`, `SIGTERM`, and `KeyboardInterrupt` for clean server termination.
- **Comprehensive Logging:** Detailed logging for server operations, requests, and errors.
- **Modular Configuration:** Separated configuration validation and loading logic into a dedicated module.

## Installation

### From PyPI (Recommended, once published)

```bash
pip install simple-api-mock-server
```

### From Source

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/sanatladkat/simple-api-mock-server.git
    cd simple-api-mock-server
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

## 🚀 Quick Start

To get a mock server up and running quickly:

1.  **Create a file `api.json` or `api.yaml`** with the following content:

    ```yaml
    - path: /hello
      methods:
        - GET
      response:
        data:
          message: "Hello, world!"
        code: 200
    ```

2.  **Run the server** from your project root:

    ```bash
    simple-mock-server --config api.yaml
    ```

3.  **Visit:** `http://localhost:5001/hello` in your browser or API client.

## 📦 PyPI Package

You can install via pip:

```bash
pip install simple-api-mock-server
```

📄 [View on PyPI](https://pypi.org/project/simple-api-mock-server/)  # Placeholder: Update with actual PyPI link after publishing

## Usage

1.  **Create an `api.json` or `api.yaml` file:**

    This file defines your API endpoints and their responses. See the [Configuration](#configuration) section for details and examples.

2.  **Run the server:**

    ```bash
simple-mock-server --config api.json --port 5001 --debug --verbose --static-folder ./static
    ```

    **CLI Options:**
    *   `--config <path>`: Path to the API configuration file (JSON or YAML). (default: `api.json`).
    *   `--port <number>`: Port to run the server on (default: `5001`).
    *   `--host <address>`: Host to bind the server to (default: `127.0.0.1`).
    *   `--debug`: Enable Flask debug mode and hot reloading (auto-reloader for code changes).
    *   `--verbose`: Enable verbose logging.
    *   `--static-folder <path>`: Path to a static folder to serve files from (e.g., for UI assets). Static files will be served at `/static/<filename>`.

3.  **Access the mock API:**

    The server will be running at `http://127.0.0.1:5001` (or your specified port).

## ⚠️ Security Note

This mock server is intended for **development and testing purposes only**. It should not be exposed to the public internet or used in production environments, as it lacks proper authentication, authorization, and input validation safeguards beyond simulation.

## 🛠️ Configuration Reference

The configuration file (JSON or YAML) is a list of route objects. Each route object can have the following properties:

*   `path` (string, **required**): The URL path for the endpoint (e.g., `/users`, `/users/{user_id}`). Flask's route variable syntax is supported.
*   `methods` (array of strings, **required**): A list of HTTP methods this endpoint responds to (e.g., `["GET", "POST"]`).
*   `response` (object, **required**): An object defining the response to return.
    *   `data` (object or array, **required**): The JSON content to return as the response body.
        *   **Dynamic Responses:**
            *   **Route Variables:** Use `{variable_name}` in the response JSON to inject values from route variables (e.g., `"id": "{user_id}"`).
            *   **Query Parameters:** Use `{query_param:param_name}` to inject values from URL query parameters (e.g., `"message": "Hello, {query_param:name}!"`).
            *   **Request Body Parameters:** Use `{body_param:param_name}` to inject values from the JSON request body (e.g., `"received_name": "{body_param:name}"`).
        *   **Echo Request Body:** Include `"echo": true` in the `data` object to have the server return the same JSON request body it received (instead of the static data response). Useful for testing POST/PUT payloads.
    *   `code` (integer, optional): The HTTP status code to return (default: `200`). For `204 No Content` responses, the body will be empty.
    *   `delay` (number, optional): The delay in seconds before sending the response, simulating network latency (default: `0`).
    *   `headers` (object, optional): A dictionary of custom HTTP headers to include in the response (e.g., `"X-Custom-Header": "MyValue"`). Headers can also be templated.
*   `description` (string, optional): A brief description of the endpoint's purpose.
*   `tags` (array of strings, optional): A list of tags for categorizing the endpoint.
*   `auth` (object, optional): Configuration for authentication simulation.
    *   `api_key` (string, **required if `auth` is present**): The expected API key. The server will look for this in the `X-API-Key` header or `api_key` query parameter. If it doesn't match, a `401 Unauthorized` response is returned.
    *   `basic_auth` (object, optional): Basic authentication credentials (`username`, `password`). If authentication fails, a `401 Unauthorized` response with a `WWW-Authenticate: Basic realm="Authentication Required"` header is returned.
    *   `bearer_token` (string, optional): Bearer token. If authentication fails, a `401 Unauthorized` response with a `WWW-Authenticate: Bearer realm="Authentication Required"` header is returned.
    *   `skip_auth` (boolean, optional): Set to `true` to disable authentication for this endpoint.
*   `rate_limit` (object, optional): Configuration for rate limiting.
    *   `requests` (integer, **required**): Maximum number of requests allowed.
    *   `window` (integer, **required**): Time window in seconds for the rate limit.
    *   Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`) are automatically included in responses. Rate limiting is applied per client IP or API key.
*   `request_body` (object, optional): An example or schema for the expected request body (for documentation/validation).
*   `query_params` (array of objects, optional): A list of query parameters for the endpoint.
    *   `name` (string, **required**): The name of the query parameter.
    *   `required` (boolean, optional): Whether the query parameter is required (default: `false`).
    *   `type` (string, optional): The type of the query parameter (default: `string`).

### `api.yaml` Example

```yaml
- path: /
  methods:
    - GET
  description: Welcome endpoint
  tags:
    - General
  response:
    data:
      message: Welcome to the mock server!
    code: 200

- path: /api/users
  methods:
    - GET
  description: Get all users
  tags:
    - Users
  response:
    data:
      - id: 1
        name: John Doe
      - id: 2
        name: Jane Doe
    code: 200

- path: /api/users
  methods:
    - POST
  description: Create a new user
  tags:
    - Users
  request_body:
    name: string
    email: string
  response:
    data:
      message: User {body_param:name} created successfully
    code: 201

- path: /api/users/{user_id}
  methods:
    - GET
  description: Get user by ID
  tags:
    - Users
  response:
    data:
      id: "{user_id}"
      name: "User {user_id}"
    headers:
      X-User-Id: "{user_id}"
    code: 200

- path: /api/greet
  methods:
    - GET
  description: Greet a user by name from query param
  tags:
    - Utilities
  query_params:
    - name: name
      required: true
      type: string
  response:
    data:
      message: "Hello, {query_param:name}!"
    code: 200

- path: /api/protected
  methods:
    - GET
  description: Protected endpoint with API key authentication
  tags:
    - Authentication
  response:
    data:
      message: Access granted!
    code: 200
  auth:
    api_key: my-secret-api-key

- path: /api/rate-limited
  methods:
    - GET
  description: Endpoint with rate limiting enabled (2 requests per 60 seconds)
  tags:
    - Rate Limiting
  response:
    data:
      message: You are not rate limited yet!
    code: 200
  rate_limit:
    requests: 2
    window: 60
```

For a more comprehensive example, refer to the `api.json` example below.

### `api.json` Example

```json
[
  {
    "path": "/",
    "methods": ["GET"],
    "description": "Welcome endpoint",
    "tags": ["General"],
    "response": {
      "data": {"message": "Welcome to the mock server!"},
      "code": 200
    }
  },
  {
    "path": "/api/users",
    "methods": ["GET"],
    "description": "Get all users",
    "tags": ["Users"],
    "response": {
      "data": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Doe"}
      ],
      "code": 200
    }
  },
  {
    "path": "/api/users",
    "methods": ["POST"],
    "description": "Create a new user",
    "tags": ["Users"],
    "request_body": {"name": "string", "email": "string"},
    "response": {
      "data": {"message": "User {body_param:name} created successfully"},
      "code": 201
    }
  },
  {
    "path": "/api/users/{user_id}",
    "methods": ["GET"],
    "description": "Get user by ID",
    "tags": ["Users"],
    "response": {
      "data": {"id": "{user_id}", "name": "User {user_id}"},
      "headers": {"X-User-Id": "{user_id}"},
      "code": 200
    }
  },
  {
    "path": "/api/users/{user_id}",
    "methods": ["PUT"],
    "description": "Update user by ID",
    "tags": ["Users"],
    "request_body": {"name": "string"},
    "response": {
      "data": {"message": "User {user_id} updated successfully"},
      "code": 200
    }
  },
  {
    "path": "/api/users/{user_id}",
    "methods": ["DELETE"],
    "description": "Delete user by ID",
    "tags": ["Users"],
    "response": {
      "data": {},
      "code": 204
    }
  },
  {
    "path": "/api/echo",
    "methods": ["POST"],
    "description": "Echoes the request body",
    "tags": ["Utilities"],
    "response": {
      "data": {"echo": true},
      "code": 200
    }
  },
  {
    "path": "/api/greet",
    "methods": ["GET"],
    "description": "Greet a user by name from query param",
    "tags": ["Utilities"],
    "response": {
      "data": {"message": "Hello, {query_param:name}!"},
      "code": 200
    }
  },
  {
    "path": "/api/slow-response",
    "methods": ["GET"],
    "description": "Simulates a slow network response",
    "tags": ["Utilities"],
    "response": {
      "data": {"message": "This was a slow response"},
      "delay": 2,
      "code": 200
    }
  },
  {
    "path": "/api/custom-headers",
    "methods": ["GET"],
    "description": "Returns a response with custom headers",
    "tags": ["Utilities"],
    "response": {
      "data": {"message": "This response has custom headers"},
      "headers": {
        "X-Custom-Header": "MyValue",
        "Content-Type": "application/json"
      },
      "code": 200
    }
  },
  {
    "path": "/api/protected",
    "methods": ["GET"],
    "description": "Protected endpoint with API key authentication",
    "tags": ["Authentication"],
    "response": {
      "data": {"message": "Access granted!"},
      "code": 200
    },
    "auth": {"api_key": "my-secret-api-key"}
  },
  {
    "path": "/api/basic-auth",
    "methods": ["GET"],
    "description": "Protected endpoint with Basic authentication",
    "tags": ["Authentication"],
    "response": {
      "data": {"message": "Basic Auth successful!"},
      "code": 200
    },
    "auth": {"basic_auth": {"username": "user", "password": "pass"}}
  },
  {
    "path": "/api/bearer-token",
    "methods": ["GET"],
    "description": "Protected endpoint with Bearer token authentication",
    "tags": ["Authentication"],
    "response": {
      "data": {"message": "Bearer Token successful!"},
      "code": 200
    },
    "auth": {"bearer_token": "my-secret-token"}
  },
  {
    "path": "/api/public",
    "methods": ["GET"],
    "description": "Public endpoint without authentication",
    "tags": ["Authentication"],
    "response": {
      "data": {"message": "This is a public endpoint!"},
      "code": 200
    },
    "auth": {"skip_auth": true}
  },
  {
    "path": "/api/error",
    "methods": ["GET"],
    "description": "Simulates an internal server error",
    "tags": ["Error Simulation"],
    "response": {
      "data": {"message": "Something went wrong!"},
      "code": 500
    }
  },
  {
    "path": "/api/not-found",
    "methods": ["GET"],
    "description": "Simulates a resource not found error",
    "tags": ["Error Simulation"],
    "response": {
      "data": {"message": "Resource not found!"},
      "code": 404
    }
  },
  {
    "path": "/api/rate-limited",
    "methods": ["GET"],
    "description": "Endpoint with rate limiting enabled (2 requests per 60 seconds)",
    "tags": ["Rate Limiting"],
    "response": {
      "data": {"message": "You are not rate limited yet!"},
      "code": 200
    },
    "rate_limit": {"requests": 2, "window": 60}
  }
]
```

## Testing

To run the unit and integration tests, navigate to the project root and execute:

```bash
pip install ".[dev]" # Install development dependencies (requests, pytest) for running tests and contributing to development.
pytest
```

## ❗ Troubleshooting



## Versioning and Changelog

See the [CHANGELOG.md](CHANGELOG.md) for details on releases and changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.