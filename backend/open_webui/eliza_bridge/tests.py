import pytest
import asyncio
from unittest.mock import patch, MagicMock

from open_webui.eliza_bridge.client import ElizaOrchestratorClient
from open_webui.eliza_bridge.registry import DecentralizedOrchestratorRegistry, AgentNode

@pytest.mark.asyncio
async def test_registry_and_client():
    registry = DecentralizedOrchestratorRegistry()
    registry.register_node("pop-os", "http://100.91.238.121:3000", ["trading"])

    target_node = registry.get_best_node_for_task("trading")
    assert target_node is not None
    assert target_node.node_id == "pop-os"

    client = ElizaOrchestratorClient()

    with patch("aiohttp.ClientSession.post") as mock_post:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status = 200
        # Mock json() to return an awaitable
        future = asyncio.Future()
        future.set_result([{"text": "Trade executed"}])
        mock_response.json.return_value = future

        # Mock the context manager
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await client.send_message("fannymae", "buy BTC", target_node.endpoint)
        assert result == "Trade executed"
