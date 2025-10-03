import pytest
import json
from simple_mock_server.config_parser import load_and_validate_config, ValidationError

def test_valid_config(tmp_path):
    config = [{
        "path": "/hello",
        "methods": ["GET"],
        "response": {"data": {"message": "Hi"}}
    }]
    file = tmp_path / "api.json"
    file.write_text(json.dumps(config))

    result = load_and_validate_config(str(file))
    assert isinstance(result, list)
    assert result[0]["path"] == "/hello"

def test_invalid_missing_required(tmp_path):
    config = [{"methods": ["GET"], "response": {"data": {}}}]  # Missing 'path'
    file = tmp_path / "api.json"
    file.write_text(json.dumps(config))

    with pytest.raises(Exception, match="Invalid api.json:"):
        load_and_validate_config(str(file))

def test_invalid_json_format(tmp_path):
    file = tmp_path / "api.json"
    file.write_text("{\"invalid json")

    with pytest.raises(ValueError, match="Failed to parse"):
        load_and_validate_config(str(file))

def test_valid_yaml_config(tmp_path):
    config = """- path: /hello
  methods:
    - GET
  response:
    data:
      message: Hi"""
    file = tmp_path / "api.yaml"
    file.write_text(config)

    result = load_and_validate_config(str(file))
    assert isinstance(result, list)
    assert result[0]["path"] == "/hello"