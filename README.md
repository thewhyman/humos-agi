# HumOS AGI

Health care data platform that uses MCP servers from systems like EPIC and also exposes MCP servers for others to push the data to the platform.

## Project Overview

HumOS is a healthcare data integration platform built on the Model Context Protocol (MCP) standard, enabling AI systems to seamlessly interact with healthcare data. The platform serves as both a consumer of MCP servers (connecting to systems like Epic) and a provider of MCP servers (exposing healthcare data to other applications).

## Features

- **MCP Client for FHIR Resources**: Connect to any FHIR-enabled MCP server to access healthcare data
- **JWT Authentication**: Secure access to healthcare systems using industry-standard authentication
- **Complete FHIR Resource Support**: Access patients, observations, medications, conditions and more
- **Standards Compliant**: Built following FHIR and MCP specifications

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- Access to a FHIR MCP server (or Epic FHIR API with proper credentials)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file from the template:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file with your configuration settings

### Configuration

The application uses the following environment variables:

- `FHIR_MCP_SERVER_URL`: URL of the FHIR MCP server
- `FHIR_CLIENT_ID`: Client ID for authentication (if required)
- `PRIVATE_KEY_PATH`: Path to your private key file for JWT authentication

### Running the Demo

The project includes a demonstration client that shows how to interact with a FHIR MCP server:

```
npm start
```

### Key Components

- **fhir-mcp-client.js**: Core client library for connecting to FHIR MCP servers
- **index.js**: Demonstration of client usage with practical examples
- **private.pem**: Your private key for JWT authentication
- **certificate.pem**: Your public certificate for registration with FHIR servers

## Usage Examples

```javascript
// Initialize the client
const client = new FHIRMCPClient({
  serverUrl: 'https://fhir-mcp.example.com/api',
  clientId: 'your-client-id',
  privateKeyPath: './private.pem',
  debug: true
});

// Search for patients
const patients = await client.searchPatients({ 
  name: 'Smith', 
  max_results: 5 
});

// Get observations for a patient
const observations = await client.getObservations('patient123', 'vital-signs');

// Get conditions for a patient
const conditions = await client.getConditions('patient123');
```

## License

MIT

## Security Note

This project uses certificate-based authentication. Be careful to:
- Never commit your private key to version control
- Protect your private key file with appropriate permissions
- Rotate your certificates periodically following security best practices
