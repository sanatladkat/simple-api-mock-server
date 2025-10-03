import time
from collections import deque
import threading
from flask import jsonify, request, Response, Request
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

rate_limit_history: Dict[str, deque] = {}
rate_limit_lock = threading.Lock()

def _get_client_id(request: "Request", auth_config: Optional[Dict[str, Any]]) -> str:
    """Extracts the client ID from the request based on API key or IP address."""
    if auth_config and auth_config.get('api_key'):
        return request.headers.get('X-API-Key') or request.args.get('api_key') or request.remote_addr
    return request.remote_addr

def handle_rate_limiting(response_config: Dict[str, Any], request: "Request", route_template_path: str) -> Tuple[Optional[Response], str]:
    """Handles rate limiting logic and returns a response if rate limit is exceeded."""
    rate_limit_config = response_config.get('rate_limit')
    auth_config = response_config.get('auth')
    client_id = _get_client_id(request, auth_config)
    endpoint_key = f"{request.method}_{route_template_path}_{client_id}"

    if not rate_limit_config:
        return None, endpoint_key

    with rate_limit_lock:
        if endpoint_key not in rate_limit_history:
            rate_limit_history[endpoint_key] = deque()

        current_time = time.time()
        window = rate_limit_config['window']
        requests_in_window = rate_limit_history[endpoint_key]

        while requests_in_window and requests_in_window[0] <= current_time - window:
            requests_in_window.popleft()

        if len(requests_in_window) >= rate_limit_config['requests']:
            logger.warning(f"Rate limit exceeded for client '{client_id}' on {request.method} {request.path}")
            first_request_time = requests_in_window[0]
            time_to_reset = int(window - (current_time - first_request_time))
            
            resp = jsonify({'error': 'Too Many Requests'})
            resp.status_code = 429
            resp.headers['X-RateLimit-Limit'] = str(rate_limit_config['requests'])
            resp.headers['X-RateLimit-Remaining'] = '0'
            resp.headers['Retry-After'] = str(max(0, time_to_reset))
            return resp, endpoint_key

        requests_in_window.append(current_time)

    return None, endpoint_key
