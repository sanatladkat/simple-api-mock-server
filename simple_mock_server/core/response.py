import json
from flask import jsonify, request, Response, Request
import jsonschema
import logging
from typing import Optional, Tuple, Dict, Any
from .rate_limiter import rate_limit_history, rate_limit_lock

logger = logging.getLogger(__name__)

def apply_templating(data: Any, kwargs: Dict[str, Any], request_args: Dict[str, Any], request_body_params: Optional[Dict[str, Any]] = None) -> Any:
    """Recursively applies templating to string values in a dict or list."""
    if request_body_params is None:
        request_body_params = {}

    if isinstance(data, str):
        # Handle route variables
        for key, value in kwargs.items():
            data = data.replace(f'{{{key}}}', str(value))
        # Handle query parameters
        for key, value in request_args.items():
            data = data.replace(f'{{query_param:{key}}}', str(value))
        # Handle request body parameters
        for key, value in request_body_params.items():
            data = data.replace(f'{{body_param:{key}}}', str(value))
        return data
    elif isinstance(data, list):
        return [apply_templating(item, kwargs, request_args, request_body_params) for item in data]
    elif isinstance(data, dict):
        return {key: apply_templating(value, kwargs, request_args, request_body_params) for key, value in data.items()}
    return data

def validate_request_body(response_config: Dict[str, Any], request: "Request") -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Response, int]]]:
    """Validates the incoming request body against the defined schema."""
    request_body_params = {}
    if request.is_json:
        try:
            request_body_params = request.get_json()
            request_body_schema = response_config.get('request_body')
            if request_body_schema:
                jsonschema.validate(instance=request_body_params, schema=request_body_schema)
            return request_body_params, None # Return params and no error
        except jsonschema.ValidationError as e:
            logger.warning(f"Request body validation failed: {e.message}")
            return None, (jsonify({"error": "Bad Request", "message": f"Request body validation failed: {e.message}"}), 400)
        except Exception as e:
            logger.warning(f"Could not parse JSON request body: {e}")
            return None, (jsonify({"error": "Bad Request", "message": "Malformed JSON in request body."}), 400)
    return request_body_params, None # Not JSON, return empty params and no error

def prepare_response(response_config: Dict[str, Any], kwargs: Dict[str, Any], request: "Request", endpoint_key: Optional[str] = None, request_body_params: Optional[Dict[str, Any]] = None) -> Response:
    """Prepares the Flask response object based on response_config."""
    if request_body_params is None:
        request_body_params = {}

    response_data = response_config.get('data', {})
    response_code = response_config.get('code', 200)
    response_headers = response_config.get('headers', {}).copy()

    rate_limit_config = response_config.get('rate_limit')
    if rate_limit_config and endpoint_key:
        with rate_limit_lock:
            if endpoint_key in rate_limit_history:
                response_headers['X-RateLimit-Limit'] = str(rate_limit_config['requests'])
                response_headers['X-RateLimit-Remaining'] = str(rate_limit_config['requests'] - len(rate_limit_history[endpoint_key]))

    json_body = request.get_json(silent=True) or {}

    templated_response_data = apply_templating(response_data, kwargs, request.args, json_body)
    templated_response_headers = apply_templating(response_headers, kwargs, request.args, json_body)

    if isinstance(templated_response_data, dict) and templated_response_data.get('echo') and request.is_json:
        templated_response_data = json_body

    if response_code == 204:
        resp = Response('', status=204)
        if 'Content-Type' in resp.headers:
            del resp.headers['Content-Type']
    else:
        resp = Response(json.dumps(templated_response_data), mimetype='application/json')
        resp.status_code = response_code

    for header, value in templated_response_headers.items():
        resp.headers[header] = value

    return resp