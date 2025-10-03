import base64
from flask import jsonify, request, Response, Request
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def _unauthorized_response(message: str, headers: Optional[Dict[str, str]] = None) -> Tuple[Response, int]:
    """Creates a 401 Unauthorized response."""
    response = jsonify({"error": "Unauthorized", "message": message})
    response.status_code = 401
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response, 401

def _check_api_key(auth_config: Dict[str, Any], request: "Request") -> Optional[Tuple[Response, int]]:
    """Checks for a valid API key."""
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not api_key or api_key != auth_config['api_key']:
        logger.warning(f"Unauthorized API Key access to {request.path}")
        return _unauthorized_response("Invalid or missing API key")
    return None

def _check_basic_auth(auth_config: Dict[str, Any], auth_header: str, request: "Request") -> Optional[Tuple[Response, int]]:
    """Checks for valid Basic authentication credentials."""
    if not auth_header or not auth_header.lower().startswith('basic '):
        logger.warning(f"Missing Basic Auth header for {request.path}")
        return _unauthorized_response("Missing Basic authentication header", {'WWW-Authenticate': 'Basic realm="Authentication Required"'})

    try:
        encoded_credentials = auth_header.split(' ', 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        if username != auth_config['basic_auth']['username'] or password != auth_config['basic_auth']['password']:
            logger.warning(f"Invalid Basic Auth credentials for {request.path}")
            return _unauthorized_response("Invalid Basic authentication credentials")
    except Exception:
        logger.exception(f"Invalid Basic Auth header format for {request.path}")
        return _unauthorized_response("Invalid Basic authentication header format")
    return None

def _check_bearer_token(auth_config: Dict[str, Any], auth_header: str, request: "Request") -> Optional[Tuple[Response, int]]:
    """Checks for a valid Bearer token."""
    if not auth_header or not auth_header.lower().startswith('bearer '):
        logger.warning(f"Missing Bearer Token header for {request.path}")
        return _unauthorized_response("Missing Bearer authentication header", {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})

    token = auth_header.split(' ', 1)[1]
    if token != auth_config['bearer_token']:
        logger.warning(f"Invalid Bearer Token for {request.path}")
        return _unauthorized_response("Invalid Bearer token")
    return None

def check_authentication(response_config: Dict[str, Any], request: "Request", route_template_path: str) -> Optional[Tuple[Response, int]]:
    """
    Handles authentication logic for a given request based on the route's configuration.

    Args:
        response_config: The response configuration for the current route.
        request: The incoming Flask request object.
        route_template_path: The template path of the route being accessed.

    Returns:
        An optional tuple containing a Flask Response object and a status code if authentication fails,
        otherwise None.
    """
    auth_config = response_config.get('auth')
    if not auth_config or auth_config.get('skip_auth'):
        return None

    auth_header = request.headers.get('Authorization')

    if auth_config.get('api_key'):
        return _check_api_key(auth_config, request)
    
    if auth_config.get('basic_auth'):
        return _check_basic_auth(auth_config, auth_header, request)

    if auth_config.get('bearer_token'):
        return _check_bearer_token(auth_config, auth_header, request)

    return None
