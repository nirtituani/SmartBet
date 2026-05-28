import pytest
from app.core import cache as cache_module


@pytest.fixture(autouse=True)
def clear_mem():
    cache_module._mem.clear()
    yield
    cache_module._mem.clear()


@pytest.mark.asyncio
async def test_get_missing_returns_none():
    result = await cache_module.get_cached("missing_key")
    assert result is None


@pytest.mark.asyncio
async def test_set_then_get_returns_value():
    await cache_module.set_cached("k1", {"data": 42}, ttl=60)
    result = await cache_module.get_cached("k1")
    assert result == {"data": 42}


@pytest.mark.asyncio
async def test_expired_entry_returns_none():
    import time
    cache_module._mem["expired"] = ({"x": 1}, time.time() - 1)
    result = await cache_module.get_cached("expired")
    assert result is None
