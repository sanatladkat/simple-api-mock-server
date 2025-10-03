import pytest
import json
from unittest.mock import mock_open, patch
from simple_mock_server.server import create_mock_server
from simple_mock_server.core.metrics import reset_metrics
from jsonschema import ValidationError



@pytest.fixture
def mock_config_file():
    # Create a dummy config file for testing
    config_content = [
        {
            "path": "/test",
            "methods": ["GET"],
            "response": {"data": {"message": "Test GET"}}
        },
        {
            "path": "/test",
            "methods": ["POST"],
            "response": {"data": {"message": "Test POST"}, "code": 201}
        },
        {
            "path": "/another",
            "methods": ["GET"],
            "response": {"data": {"message": "Another GET"}, "delay": 1}
        }
    ]
    with patch('builtins.open', mock_open(read_data=json.dumps(config_content))):
        yield

@pytest.fixture
def mock_invalid_config_file():
    # Create an invalid config file for testing schema validation
    config_content = [
        {
            "path": "/invalid",
            "methods": ["GET"],
            "response": "not an object" # Invalid response type
        }
    ]
    with patch('builtins.open', mock_open(read_data=json.dumps(config_content))):
        yield

@pytest.fixture
def mock_conflict_config_file():
    # Create a config file with a route conflict
    config_content = [
        {
            "path": "/conflict",
            "methods": ["GET"],
            "response": {"data": {"message": "First"}}
        },
        {
            "path": "/conflict",
            "methods": ["GET"],
            "response": {"data": {"message": "Second"}}
        }
    ]
    with patch('builtins.open', mock_open(read_data=json.dumps(config_content))):
        yield

@pytest.fixture
def client(tmp_path):
    # Create a temporary api.json for the test client
    config_content = [
        {
            "path": "/",
            "methods": ["GET"],
            "response": {"data": {"message": "Welcome!"}, "code": 200}
        },
        {
            "path": "/users/{user_id}",
            "methods": ["GET"],
            "response": {"data": {"id": "{user_id}", "name": "User {user_id}"}, "headers": {"X-User-Id": "{user_id}"}, "code": 200}
        },
        {
            "path": "/echo",
            "methods": ["POST"],
            "response": {"data": {"echo": True}, "code": 200}
        },
        {
            "path": "/protected",
            "methods": ["GET"],
            "response": {"data": {"message": "Access granted!"}, "code": 200},
            "auth": {"api_key": "test-api-key"}
        },
        {
            "path": "/basic-auth",
            "methods": ["GET"],
            "response": {"data": {"message": "Basic Auth successful!"}, "code": 200},
            "auth": {"basic_auth": {"username": "user", "password": "pass"}}
        },
        {
            "path": "/bearer-auth",
            "methods": ["GET"],
            "response": {"data": {"message": "Bearer Token successful!"}, "code": 200},
            "auth": {"bearer_token": "test-bearer-token"}
        },
        {
            "path": "/slow",
            "methods": ["GET"],
            "response": {"data": {"message": "Slow response"}, "delay": 0.5, "code": 200}
        },
        {
            "path": "/error",
            "methods": ["GET"],
            "response": {"data": {"message": "Internal Server Error"}, "code": 500}
        },
        {
            "path": "/custom-header",
            "methods": ["GET"],
            "response": {"data": {"message": "Custom header here"}, "headers": {"X-Test-Header": "TestValue"}, "code": 200}
        },
        {
            "path": "/status-204",
            "methods": ["DELETE"],
            "response": {"data": {}, "code": 204}
        },
        {
            "path": "/rate-limited",
            "methods": ["GET"],
            "response": {"data": {"message": "You are not rate limited yet!"}, "code": 200},
            "rate_limit": {"requests": 2, "window": 60}
        }
    ]
    config_path = tmp_path / "test_api.json"
    config_path.write_text(json.dumps(config_content))
    
    reset_metrics()
    app = create_mock_server(config_path=str(config_path), host='localhost', port=5000)
    with app.test_client() as client:
        yield client

class TestConfigLoading:
    def test_create_mock_server_valid_config(self, mock_config_file):
        app = create_mock_server(config_path='dummy.json')
        # Flask's url_map contains all registered routes
        # We need to filter out Flask's internal routes like /static and /health
        registered_paths = [rule.rule for rule in app.url_map.iter_rules() if rule.endpoint not in ['static', 'health_check', 'openapi_spec', 'metrics']]
        assert len(registered_paths) == 2
        assert "/test" in registered_paths
        assert "/another" in registered_paths

    def test_create_mock_server_invalid_config(self, mock_invalid_config_file):
        with pytest.raises(Exception, match="Invalid api.json:") as excinfo:
            create_mock_server(config_path='dummy.json')
        assert isinstance(excinfo.value.__cause__, ValidationError)

    def test_create_mock_server_route_conflict(self, mock_conflict_config_file):
        with pytest.raises(Exception, match="Route conflict: GET /conflict is already defined."):
            create_mock_server(config_path='dummy.json')

class TestBasicEndpoints:
    def test_get_root(self, client):
        response = client.get("/")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json == {"message": "Welcome!"}

    def test_post_echo(self, client):
        data = {"key": "value"}
        response = client.post("/echo", json=data)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json == data

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json['status'] == "ok"
        assert "uptime_seconds" in response.json

    def test_openapi_spec(self, client):
        """Test the OpenAPI spec endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json['openapi'] == "3.0.0"
        assert "/protected" in response.json['paths']

class TestAuthEndpoints:
    @pytest.mark.parametrize("auth_header,status_code", [
        ({"Authorization": "Basic dXNlcjpwYXNz"}, 200),
        ({"Authorization": "Basic d3Jvbmc6d3Jvbmc="}, 401),
    ])
    def test_basic_auth(self, client, auth_header, status_code):
        response = client.get("/basic-auth", headers=auth_header)
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"

    @pytest.mark.parametrize("auth_header,status_code", [
        ({"Authorization": "Bearer test-bearer-token"}, 200),
        ({"Authorization": "Bearer wrong-token"}, 401),
    ])
    def test_bearer_auth(self, client, auth_header, status_code):
        response = client.get("/bearer-auth", headers=auth_header)
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"

    def test_protected_access_unauthorized(self, client):
        response = client.get("/protected")
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        assert response.json == {"error": "Unauthorized", "message": "Invalid or missing API key"}

    def test_protected_access_authorized(self, client):
        headers = {"X-API-Key": "test-api-key"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json == {"message": "Access granted!"}

    def test_api_key_in_query_param(self, client):
        """Test that API key auth succeeds via query parameter."""
        response = client.get("/protected?api_key=test-api-key")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json == {"message": "Access granted!"}

class TestRateLimiting:
    def test_rate_limiting(self, client):
        """Test rate limiting behavior and X-RateLimit headers."""
        # First two requests should succeed
        response1 = client.get("/rate-limited")
        assert response1.status_code == 200, f"Expected 200 OK, got {response1.status_code}"
        assert response1.headers['X-RateLimit-Limit'] == '2'
        assert response1.headers['X-RateLimit-Remaining'] == '1'

        response2 = client.get("/rate-limited")
        assert response2.status_code == 200, f"Expected 200 OK, got {response2.status_code}"
        assert response2.headers['X-RateLimit-Limit'] == '2'
        assert response2.headers['X-RateLimit-Remaining'] == '0'

        # Third request should be rate-limited
        response3 = client.get("/rate-limited")
        assert response3.status_code == 429, f"Expected 429 Too Many Requests, got {response3.status_code}"
        assert response3.json == {"error": "Too Many Requests"}
        assert response3.headers['X-RateLimit-Limit'] == '2'
        assert response3.headers['X-RateLimit-Remaining'] == '0'
        assert 'Retry-After' in response3.headers, "Missing 'Retry-After' header in rate-limited response"

class TestSpecialResponses:
    def test_error_response(self, client):
        response = client.get("/error")
        assert response.status_code == 500, f"Expected 500 Internal Server Error, got {response.status_code}"
        assert response.json == {"message": "Internal Server Error"}

    def test_custom_header(self, client):
        response = client.get("/custom-header")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert 'X-Test-Header' in response.headers, "Missing expected custom header"
        assert response.headers['X-Test-Header'] == "TestValue"

    def test_404_unknown_route(self, client):
        """Test that accessing an unknown route returns a 404 JSON response."""
        response = client.get("/non-existent-route")
        assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
        assert response.json == {"error": "Not Found", "message": "The requested URL /non-existent-route was not found on the server."}
        assert response.headers['Content-Type'] == 'application/json', "Incorrect Content-Type for 404 response"

    def test_204_no_content(self, client):
        """Test that a 204 No Content response has an empty body."""
        response = client.delete("/status-204")
        assert response.status_code == 204, f"Expected 204 No Content, got {response.status_code}"
        assert response.data == b'', "Response body should be empty for 204 response"
        assert 'Content-Type' not in response.headers, "Content-Type header should not be present for 204 response"

class TestTemplating:
    def test_get_user_with_id(self, client):
        response = client.get("/users/123")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.json == {"id": "123", "name": "User 123"}

    def test_templated_header(self, client):
        """Test that headers can be templated with route variables."""
        response = client.get("/users/456")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert response.headers['X-User-Id'] == "456"

class TestMetrics:
    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint."""
        client.get("/")
        client.get("/users/123")
        response = client.get("/metrics")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert b'http_requests_total 2' in response.data
        assert b'http_requests_by_path_total{path="/"} 1' in response.data
        assert b'http_requests_by_path_total{path="/users/123"} 1' in response.data
        assert b'http_requests_by_method_total{method="GET"} 2' in response.data