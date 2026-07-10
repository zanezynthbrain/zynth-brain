import pytest

from utils.tools import http_get, http_post, read_file, validate_json, write_file


async def test_http_get_is_mocked_without_network_flag():
    result = await http_get("https://example.com/search", params={"q": "test"})
    assert result.ok is True
    assert result.mocked is True
    assert result.data["url"] == "https://example.com/search"


async def test_http_post_is_mocked_without_network_flag():
    result = await http_post("https://example.com/webhook", payload={"a": 1})
    assert result.ok is True
    assert result.mocked is True


def test_write_then_read_file_roundtrip():
    write_result = write_file("test_artifacts/sample.txt", "hello zynth")
    assert write_result.ok is True

    read_result = read_file("test_artifacts/sample.txt")
    assert read_result.ok is True
    assert read_result.data == "hello zynth"


def test_read_missing_file_returns_error():
    result = read_file("does/not/exist.txt")
    assert result.ok is False
    assert "not found" in result.error.lower()


def test_path_traversal_is_rejected():
    result = write_file("../../escape.txt", "nope")
    assert result.ok is False


def test_validate_json_success():
    schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}}
    result = validate_json('{"a": 1}', schema)
    assert result.ok is True
    assert result.data == {"a": 1}


def test_validate_json_reports_schema_violation():
    schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}}
    result = validate_json('{"a": "not-an-int"}', schema)
    assert result.ok is False
    assert result.error


def test_validate_json_reports_malformed_json():
    schema = {"type": "object"}
    result = validate_json("{not json", schema)
    assert result.ok is False
    assert "Invalid JSON" in result.error
