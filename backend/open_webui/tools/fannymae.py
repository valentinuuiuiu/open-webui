"""
FannyMae Tools Integration for Decentralized Orchestration.

Exposes FannyMae as a primary intelligent router that leverages the
Eliza-OS microservices running across the Tailscale network.
"""

import logging
from typing import Optional
from fastapi import Request

from open_webui.eliza_bridge.client import eliza_client
from open_webui.eliza_bridge.registry import registry

log = logging.getLogger(__name__)

async def ask_fannymae(
    request_text: str,
    required_capability: str = "trading",
    agent_id: str = "fannymae",
    __request__: Request = None,
    __user__: dict = None,
) -> str:
    """
    Route a complex orchestration, trading, or decentralized intelligence task
    to the specialized FannyMae Eliza-OS microservice. The Iron Hand Orchestrator
    will automatically find an active node on the Tailscale network capable of handling it.

    :param request_text: The user's query or instruction for FannyMae.
    :param required_capability: The capability required to process this task (e.g., trading, security).
    :param agent_id: The specific agent ID running on the Eliza node (default: fannymae).
    :return: The response from the FannyMae agent.
    """
    if __user__ is None:
        return "Error: User context not available."

    user_email = __user__.get("email", "unknown_user")

    # 1. Orchestrator looks for the best node
    log.info(f"Looking for an active decentralized node with capability '{required_capability}'...")
    target_node = registry.get_best_node_for_task(required_capability)

    if not target_node:
        return f"Orchestrator Error: No active nodes found on the network with capability '{required_capability}'. Please ensure Tailscale devices (e.g. pop-os, kali) are online."

    log.info(f"Routing request to Eliza OS node '{target_node.node_id}' at {target_node.endpoint} (agent: {agent_id}) for user: {user_email}")

    # 2. Dispatch to the node
    response = await eliza_client.send_message(
        agent_id=agent_id,
        message=request_text,
        node_endpoint=target_node.endpoint,
        user_id=user_email
    )

    if response is None:
        return f"Error: FannyMae (Eliza OS) on node {target_node.node_id} is currently offline or unreachable."

    return f"[Decentralized Node: {target_node.node_id}] {response}"
