# HumOS FHIR Health Agent

A Python-based AI-enabled agent platform for accessing, analyzing, and interpreting FHIR healthcare data within the HumOS AGI ecosystem.

## Project Overview

HumOS FHIR Health Agent is a healthcare data integration platform built on the Model Context Protocol (MCP) standard, enabling AI systems to seamlessly interact with healthcare data. The platform provides a comprehensive Python implementation with both a FastMCP server for exposing FHIR data and a client for consuming that data.

## Features

### Comprehensive Medical Data Access

- **Patient Demographics**: Retrieve detailed patient information with proper formatting
- **Medical Conditions**: Access current and historical health problems with status tracking
- **Medications**: View prescribed medications with dosage instructions and status
- **Observations & Lab Results**: Access vital signs, lab values, and other clinical measurements
- **Allergies & Intolerances**: View patient allergies with reaction details and criticality levels
- **Medical Procedures**: Access surgical and therapeutic interventions
- **Immunizations**: Track vaccination history and status
- **Diagnostic Reports**: Retrieve imaging, pathology, and other clinical reports
- **Care Plans**: Access treatment plans with goals and timeframes
- **Vital Signs Dashboard**: Specialized endpoint for viewing patient vital signs using LOINC codes

### Advanced Features

- **Patient Summaries**: Generate comprehensive text summaries of patient medical data
- **Personalized Health Recommendations**: AI-generated health advice based on patient's specific medical profile
- **Structured Data Access**: Retrieve all medical data in an organized dictionary format
- **Interactive Agent**: Conversational AI agent interface for natural language queries about patient data
- **Robust Mock Data System**: Built-in realistic mock data for development and testing

## Architecture

- **FastMCP Server** (`server.py`): Exposes FHIR data through a Model Context Protocol interface
- **FHIR Client** (`fhir_client.py`): Provides methods to query the FHIR MCP server
- **uAgent** (`agent.py`): Integrates with MCP to provide a conversational interface to health data

## Getting Started

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- Access to a FHIR server (optional - includes mock data mode)

### Installation

1. Clone this repository
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install httpx mcp uagents
   ```

### Configuration

The application supports the following environment variables:

- `FHIR_MCP_SERVER_URL`: URL of the FHIR server (default: `https://hapi.fhir.org/baseR4`)
- `USE_MOCK_DATA`: Set to "False" to use a real FHIR server (default: "True")

### Running the Agent

```bash
# Start the FHIR agent
python agent.py
```

## Using Mock Data

This project includes comprehensive mock data for testing and development. By default, mock data mode is enabled, providing realistic patient profiles without requiring a connection to a FHIR server.

### Mock Patient Profiles

- **Patient 1**: Respiratory conditions (asthma, allergies) with appropriate medications
- **Patient 2**: Cardiovascular focus (CAD, atrial fibrillation) with heart medications and renal involvement
- **Patient 3**: Neurological and GI conditions (migraines, IBS) with relevant medications
- **Patient 4**: Complex chronic conditions (COPD, osteoporosis, hypothyroidism, chronic pain)

To use with real data, set the environment variable:
```bash
export USE_MOCK_DATA="False"
```

## Code Structure

### Key Components

- **server.py**: FastMCP server implementation with FHIR data access methods
- **fhir_client.py**: Client library for connecting to the FHIR MCP server
- **agent.py**: uAgent implementation for conversational interface

## Usage Examples

```python
# Direct use of the FHIR client
from fhir_client import FHIRClient

async def example():
    client = FHIRClient()
    
    # Search for patients
    patients = await client.search_patients("Smith")
    
    # Get conditions for a patient
    conditions = await client.get_conditions("patient123")
    
    # Get comprehensive patient summary
    summary = await client.get_patient_summary("patient123")
```

## Security Considerations

- This implementation uses the public HAPI FHIR test server by default
- For production use, configure appropriate authentication mechanisms
- Ensure proper handling of PHI (Protected Health Information) in compliance with regulations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
