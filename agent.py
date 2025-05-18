"""HumOS Personalized Health Agent

A conversational AI agent built on uAgents that provides intelligent access to FHIR healthcare data.

This agent integrates with the FHIR MCP server to retrieve, analyze, and present medical information
in a conversational format. It can access comprehensive patient data including:

- Patient demographics and personal information
- Medical conditions and diagnoses
- Medications and treatment plans
- Observations and laboratory results
- Allergies and contraindications
- Medical procedures and interventions
- Immunization history and status
- Diagnostic reports and clinical findings
- Care plans and treatment goals
- Vital signs with specialized formatting

The agent employs AI-powered natural language understanding to interpret user queries
about health data and respond with relevant information from FHIR resources.

Features:
- Mock data support for development and testing
- Configurable FHIR server connection
- Comprehensive medical data access
- Patient summary generation
- Structured data retrieval

Usage:
    python agent.py

Environment Variables:
    FHIR_MCP_SERVER_URL: URL of FHIR server (default: https://hapi.fhir.org/baseR4)
    USE_MOCK_DATA: Set to "False" to use real FHIR server (default: "True")
"""

import mailbox
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
agent = Agent(name="humos_personalized_health_agent", port=8002, mailbox=True)

# Include protocols from the adapter
for protocol in mcp_adapter.protocols:
    agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    # Run the MCP adapter with the agent
    mcp_adapter.run(agent)