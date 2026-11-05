import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

log = logging.getLogger(__name__)

class AgentNode:
    def __init__(self, node_id: str, endpoint: str, capabilities: List[str]):
        self.node_id = node_id          # e.g., 'kali', 'pop-os', 'vps3273531'
        self.endpoint = endpoint        # e.g., 'http://100.91.238.121:3000'
        self.capabilities = capabilities # e.g., ['trading', 'solana', 'research']
        self.is_active = True
        self.last_seen = datetime.now()

class DecentralizedOrchestratorRegistry:
    """
    'Mână de fier' (Iron Hand) registry for tracking, validating, and selecting
    decentralized agent microservices across a Tailscale/mesh network.
    """
    def __init__(self):
        self.nodes: Dict[str, AgentNode] = {}
        self.health_check_interval = 30 # seconds

    def register_node(self, node_id: str, endpoint: str, capabilities: List[str]):
        """Register a new Eliza agent node on the network."""
        log.info(f"Registering node '{node_id}' at {endpoint} with capabilities: {capabilities}")
        self.nodes[node_id] = AgentNode(node_id, endpoint, capabilities)

    def remove_node(self, node_id: str):
        """Remove an unresponsive or decommissioned node."""
        if node_id in self.nodes:
            log.info(f"Removing node '{node_id}' from registry.")
            del self.nodes[node_id]

    def get_best_node_for_task(self, required_capability: str) -> Optional[AgentNode]:
        """
        Intelligently select the best active node that has the required capability.
        (Future logic: load balancing, lowest latency, etc.)
        """
        active_capable_nodes = [
            node for node in self.nodes.values()
            if node.is_active and required_capability in node.capabilities
        ]

        if not active_capable_nodes:
            log.warning(f"No active nodes found for capability: {required_capability}")
            return None

        # Basic load balancing: just return the most recently seen node for now
        # A true orchestrator would route based on load metrics gathered via health checks.
        return sorted(active_capable_nodes, key=lambda x: x.last_seen, reverse=True)[0]

    async def _ping_node(self, node: AgentNode, session: aiohttp.ClientSession):
        """Perform a lightweight health check on the Eliza node."""
        # Typically Eliza has a health or root endpoint, we use root '/' for simplicity
        url = f"{node.endpoint}/"
        try:
            async with session.get(url, timeout=5.0) as response:
                if response.status == 200:
                    node.is_active = True
                    node.last_seen = datetime.now()
                    log.debug(f"Node {node.node_id} is healthy.")
                else:
                    node.is_active = False
                    log.warning(f"Node {node.node_id} returned unhealthy status: {response.status}")
        except Exception as e:
            node.is_active = False
            log.warning(f"Node {node.node_id} is unreachable: {e}")

    async def start_health_checks(self):
        """Background task to continuously monitor the health of all registered nodes."""
        log.info("Starting decentralized orchestrator health checks...")
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self._ping_node(node, session) for node in self.nodes.values()]
                if tasks:
                    await asyncio.gather(*tasks)
                await asyncio.sleep(self.health_check_interval)

# Global registry instance
registry = DecentralizedOrchestratorRegistry()

# Initialize with known Tailscale nodes for testing/demo purposes based on provided context
registry.register_node("pop-os", "http://100.91.238.121:3000", ["trading", "solana", "research"])
registry.register_node("kali", "http://100.92.164.32:3000", ["security", "pentest"])
registry.register_node("vps", "http://100.75.36.5:3000", ["database", "storage"])
