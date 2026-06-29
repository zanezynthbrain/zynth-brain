import asyncio

from utils.state import SharedMemory


async def test_set_get_roundtrip():
    memory = SharedMemory(client_brief={"company": "Acme"})
    assert await memory.get("client_brief") == {"company": "Acme"}

    await memory.set("research_seo", {"keywords": ["a", "b"]})
    assert await memory.get("research_seo") == {"keywords": ["a", "b"]}
    assert await memory.get("missing_namespace", default="fallback") == "fallback"


async def test_update_merges_dict_namespace():
    memory = SharedMemory()
    await memory.update("copywriter", ad_copy=[1, 2])
    await memory.update("copywriter", linkedin_article={"title": "x"})
    result = await memory.get("copywriter")
    assert result == {"ad_copy": [1, 2], "linkedin_article": {"title": "x"}}


async def test_token_tracking_accumulates():
    memory = SharedMemory()
    await memory.record_tokens(10, 20)
    await memory.record_tokens(5, 5)
    assert await memory.total_tokens() == 40


async def test_concurrent_writes_are_serialized():
    memory = SharedMemory()

    async def writer(n: int) -> None:
        await memory.set(f"agent_{n}", {"value": n})

    await asyncio.gather(*[writer(i) for i in range(20)])
    for i in range(20):
        assert await memory.get(f"agent_{i}") == {"value": i}


async def test_log_and_snapshot_capture_history():
    memory = SharedMemory()
    await memory.log("research_seo", "started")
    await memory.log("research_seo", "completed", input_tokens=10)
    snapshot = await memory.snapshot()
    assert len(snapshot["log"]) == 2
    assert snapshot["log"][1]["event"] == "completed"
    assert snapshot["log"][1]["detail"]["input_tokens"] == 10
