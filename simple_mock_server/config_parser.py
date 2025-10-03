import json
import jsonschema
from jsonschema import ValidationError
import yaml

API_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "description": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "methods": {
                "type": "array",
                "items": {"type": "string"}
            },
            "response": {
                "type": "object",
                "properties": {
                    "data": {},
                    "code": {"type": "integer"},
                    "delay": {"type": "number"},
                    "headers": {"type": "object", "patternProperties": {".*": {"type": "string"}}}
                },
                "required": ["data"],
                "additionalProperties": False
            },
            "auth": {
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                    "basic_auth": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"}
                        },
                        "required": ["username", "password"],
                        "additionalProperties": False
                    },
                    "bearer_token": {"type": "string"}
                },
                "minProperties": 1,
                "additionalProperties": False
            },
            "rate_limit": {
                "type": "object",
                "properties": {
                    "requests": {"type": "integer", "minimum": 1},
                    "window": {"type": "integer", "minimum": 1}
                },
                "required": ["requests", "window"],
                "additionalProperties": False
            },
            "request_body": {"type": "object"},
            "query_params": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "required": {"type": "boolean"},
                        "type": {"type": "string"}
                    },
                    "required": ["name"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["path", "methods", "response"],
        "additionalProperties": False
    }
}

def load_and_validate_config(config_path):
    with open(config_path, 'r') as f:
        try:
            if config_path.lower().endswith(('.yml', '.yaml')):
                routes_config = yaml.safe_load(f)
            else:
                routes_config = json.load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to parse {config_path}: {e}") from e

    try:
        jsonschema.validate(instance=routes_config, schema=API_SCHEMA)
    except ValidationError as e:
        raise Exception(f"Invalid api.json: {e.message}") from e

    return routes_config

__all__ = ["load_and_validate_config", "ValidationError", "API_SCHEMA"]
