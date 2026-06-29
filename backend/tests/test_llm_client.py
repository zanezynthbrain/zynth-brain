from utils.llm_client import LLMClient, MalformedOutputError


async def test_mock_mode_active_without_api_key():
    client = LLMClient()
    assert client.is_mocked is True


async def test_complete_returns_mock_response():
    client = LLMClient()
    response = await client.complete(system="sys", user_prompt="hello")
    assert response.mocked is True
    assert "MOCK" in response.text


async def test_complete_json_synthesizes_schema_conforming_mock():
    schema = {
        "type": "object",
        "required": ["name", "score"],
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
    }
    client = LLMClient()
    data, response = await client.complete_json(system="sys", user_prompt="give me an object", schema=schema)
    assert set(data.keys()) == {"name", "score"}
    assert isinstance(data["name"], str)
    assert isinstance(data["score"], (int, float))
    assert response.mocked is True
