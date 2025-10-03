# Changelog

## 0.3.1 - 2025-10-03

### Changed

- **Refactored Authentication:** Improved clarity, consistency, and maintainability of authentication logic by extracting helper functions, using consistent return patterns, and adding type hints.
- **Refactored Metrics:** Enhanced metrics module to use `collections.Counter` and `threading.Lock` for thread-safe and semantically clearer metric tracking.

### Fixed

- **Pylance Type Hinting:** Resolved `PylancereportInvalidTypeForm` error by correctly type-hinting Flask `request` objects as `"Request"`.

## 0.3.0 - 2025-10-03

### Added

- **YAML Configuration:** The server now supports `.yml` and `.yaml` configuration files in addition to JSON.
- **Metrics Endpoint:** A new `/metrics` endpoint exposes request counts in Prometheus format for monitoring.
- **Richer OpenAPI Specification:** The generated OpenAPI spec now includes path parameters, query parameters, and security schemes.

### Changed

- **Improved Modularity:** Refactored core logic (authentication, rate limiting, response handling) into separate modules for better organization and testability.
- **Robust Endpoint Creation:** Refactored endpoint creation to use a factory pattern, preventing potential late-binding issues in loops.

### Fixed

- **Test Isolation:** Metrics are now reset between test runs to ensure accurate and independent test results.

## 0.2.0 - 2025-10-03

### Added

- **Granular Rate Limiting:** Rate limiting now supports per-client granularity using IP address or API key as the `endpoint_key`.
- **Static File Serving:** Added `--static-folder` CLI argument to serve static files from a specified directory.
- **API Key in Query Params:** API key can now be passed via URL query parameters in addition to headers.
- **Request Body Templating:** Responses now support `{body_param:...}` syntax to inject values from the request body.
- **Method-Specific Headers:** Support for defining different custom headers per HTTP method in a route's `response`.
- **Endpoint Metadata:** `description` and `tags` fields added to the API schema for better documentation and grouping.
- **Example Request Bodies:** Optional `request_body` field can now be used to document expected payloads.
- **CORS Support:** Integrated `flask-cors` to support Cross-Origin Resource Sharing.
- **Unit Tests for `config_parser.py`:** Added targeted tests for configuration validation and schema loading.

### Changed

- **Modular Configuration:** Moved `API_SCHEMA` and validation logic to a separate `config_parser.py` module.
- **Explicit HTTP Status Codes:** All endpoints in the test fixtures now explicitly define a `code`, including 200.
- **204 Response Semantics:** Removed `mimetype` from 204 No Content responses to align with HTTP standards.
- **Optional Dev Dependencies:** `requests` and `pytest` moved to `extras_require` in `setup.py`; removed from `requirements.txt`.
- **Health Check Header:** `/health` endpoint now explicitly returns `Content-Type: application/json`.
- **Rate Limiting Pruning:** Implemented a mechanism to remove empty rate limit history entries, preventing indefinite memory growth.
- **Auth Challenge Headers:** Added `WWW-Authenticate` headers to 401 responses for Basic and Bearer authentication.

### Fixed

- **404 Handling:** Custom JSON response for unknown routes via a centralized 404 error handler.
- **Late-Binding Bug in Route Creation:** Fixed in `create_endpoint` by passing `responses` and `allowed_methods` as function arguments.
- **Thread-Safe Rate Limiting:** Introduced `threading.Lock` to protect `rate_limit_history` from race conditions.
- **Hot Reload Path Normalization:** `ConfigChangeHandler` now normalizes paths with `os.path.abspath()` and handles `on_created` events.
- **Graceful Shutdown:** Catches `KeyboardInterrupt` and ensures clean shutdown; checks for `None` observer.
- **Port Binding Errors:** Improved error messages for `OSError` (e.g., port already in use).
- **Malformed JSON Handling:** Returns `400 Bad Request` when request body contains invalid JSON.
- **Validation Error Chaining:** Properly chains `jsonschema.ValidationError` when re-raised for better traceback context.
- **README Encoding:** Ensures UTF-8 encoding when reading `README.md` during setup.
- **Packaging Fixes:** Added `MANIFEST.in` to include non-Python files in distribution.
- **Docstrings:** Added module-level docstring to `simple_mock_server/server.py`.
- **Test Refactoring:** Integration tests migrated to use Flask's `app.test_client()` and `tmp_path`.
- **Hot Reload Messaging:** Warns user if hot reload is requested but `--debug` is not enabled.

---

## 0.1.0 - 2025-10-03

### Added

- Initial release of Simple API Mock Server.
- Dynamic routing with configurable methods, paths, and responses.
- Support for route parameters and query parameters in templated responses.
- Echo request body for POST/PUT requests.
- Custom headers and response delays.
- Basic API key authentication simulation.
- JSON schema validation for `api.json`.
- Error simulation for 4xx and 5xx responses.
- Duplicate route conflict prevention.
- Built-in `/health` endpoint.
- CLI interface with support for config path, port, debug mode, and verbosity.
- Hot reloading on `api.json` changes.
- Logging for requests and server events.
- Unit and integration tests.
- Project structure: `setup.py`, `LICENSE`, `requirements.txt`.
- Initial `README.md` with setup and usage instructions.
