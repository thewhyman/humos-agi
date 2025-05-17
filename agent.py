from uagents import Agent
from uagents_adapter import MCPServerAdapter
from server import mcp
import os

# Create an MCP adapter with your MCP server
mcp_adapter = MCPServerAdapter(
    mcp_server=mcp, 
    asi1_api_key="sk_52397439fdf74a05a903b4c62fe2ef7a40e1ef72d4944323bb23b46ef1302fa7",  # Replace with your actual API key
    model="asi1-fast"  # Options: asi1-mini, asi1-extended, asi1-fast
)

# Create a uAgent
agent = Agent()

# Include protocols from the adapter
for protocol in mcp_adapter.protocols:
    agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    # Run the MCP adapter with the agent
    mcp_adapter.run(agent)