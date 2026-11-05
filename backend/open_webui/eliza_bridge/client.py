import aiohttp
import logging
from typing import Optional

log = logging.getLogger(__name__)

class ElizaOrchestratorClient:
    """
    A robust client designed to communicate with decentralized Eliza OS microservices
    running on a private network (e.g. Tailscale). It handles routing requests to
    specific node endpoints dynamically rather than a single static host.
    """
    def __init__(self):
        self.timeout = 60.0

    async def send_message(self, agent_id: str, message: str, node_endpoint: str, user_id: str = "user") -> Optional[str]:
        """
        Send a message to a specific Eliza agent microservice on a specific Tailscale node.

        :param agent_id: The specific agent ID on the Eliza node.
        :param message: The user message or task.
        :param node_endpoint: The HTTP endpoint of the specific node (e.g. http://100.91.238.121:3000)
        :param user_id: User identifier for room/session tracking.
        """
        url = f"{node_endpoint}/{agent_id}/message"
        payload = {
            "text": message,
            "userId": user_id,
            "roomId": f"openwebui_decentralized_{user_id}"
        }

        log.info(f"Dispatching task to decentralized node at {url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            return data[-1].get("text", "")
                        return str(data)
                    else:
                        error_text = await response.text()
                        log.error(f"Eliza node returned status {response.status}: {error_text}")
                        return f"Error communicating with decentralized agent: {response.status}"
        except Exception as e:
            log.error(f"Failed to reach decentralized Eliza OS node at {url}: {e}")
            return None

eliza_client = ElizaOrchestratorClient()
