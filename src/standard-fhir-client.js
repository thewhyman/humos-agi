/**
 * HumOS AGI - Standard FHIR Client
 * 
 * A simplified FHIR client implementation using the standard fhirclient library.
 * This approach follows FHIR RESTful API standards that should work with
 * most FHIR servers including Flexpa.
 */

const FHIR = require('fhirclient');
const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');
const axios = require('axios');
require('dotenv').config();

class StandardFhirClient {
  /**
   * Creates a new Standard FHIR client
   * @param {Object} config - Configuration 
   * @param {string} config.baseUrl - Base URL for FHIR server
   * @param {string} [config.clientId] - Client ID for authentication
   * @param {string} [config.privateKeyPath] - Path to private key file
   * @param {boolean} [config.debug=false] - Enable debug logging
   */
  constructor(config) {
    this.baseUrl = config.baseUrl || process.env.FHIR_MCP_SERVER_URL || 'https://api.flexpa.com/fhir';
    this.clientId = config.clientId || process.env.FHIR_CLIENT_ID;
    this.privateKeyPath = config.privateKeyPath || process.env.PRIVATE_KEY_PATH;
    this.debug = config.debug || false;
    
    this.accessToken = null;
    this.client = null;
    
    this.log('Standard FHIR Client initialized');
    this.log(`Base URL: ${this.baseUrl}`);
  }
  
  /**
   * Logs debug messages
   * @param {...any} args - Arguments to log
   */
  log(...args) {
    if (this.debug) {
      console.log('[FHIR Client]', ...args);
    }
  }
  
  /**
   * Initializes the FHIR client
   * @returns {Promise<object>} - Initialized FHIR client
   */
  async initialize() {
    try {
      // If we already have a token, use direct authentication
      if (this.accessToken) {
        this.log('Initializing with existing token');
      } else if (this.clientId && this.privateKeyPath) {
        // Try to get a token using JWT authentication
        this.log('Attempting JWT authentication');
        await this.authenticateWithJWT();
      }
      
      // Initialize the FHIR client with the server URL
      const clientOptions = {
        serverUrl: this.baseUrl
      };
      
      // Add token if available
      if (this.accessToken) {
        clientOptions.customHeaders = {
          Authorization: `Bearer ${this.accessToken}`
        };
      }
      
      this.client = FHIR.client(clientOptions);
      this.log('FHIR client initialized successfully');
      return this.client;
    } catch (error) {
      this.log('Error initializing FHIR client:', error.message);
      throw error;
    }
  }
  
  /**
   * Tries to authenticate using JWT
   * @returns {Promise<string>} - Access token
   */
  async authenticateWithJWT() {
    try {
      this.log('Authenticating with JWT');
      
      // Read private key
      const privateKey = fs.readFileSync(this.privateKeyPath, 'utf8');
      
      // Create JWT token
      const now = Math.floor(Date.now() / 1000);
      const jwtPayload = {
        iss: this.clientId,
        sub: this.clientId,
        aud: `${this.baseUrl}/auth/token`,
        jti: `${this.clientId}-${now}`,
        exp: now + 300,
        iat: now
      };
      
      const assertion = jwt.sign(jwtPayload, privateKey, { algorithm: 'RS256' });
      
      // Try different authentication endpoints
      const authEndpoints = [
        '/auth/token',
        '/oauth/token',
        '/token',
        '/oauth2/token'
      ];
      
      let tokenResponse = null;
      let errorMessage = '';
      
      for (const endpoint of authEndpoints) {
        try {
          this.log(`Trying auth endpoint: ${endpoint}`);
          
          const authUrl = new URL(endpoint, this.baseUrl).toString();
          const response = await axios.post(authUrl, {
            grant_type: 'client_credentials',
            client_assertion_type: 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            client_assertion: assertion,
            client_id: this.clientId
          }, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          });
          
          if (response.data && response.data.access_token) {
            tokenResponse = response.data;
            break;
          }
        } catch (error) {
          errorMessage = `${error.message} at ${endpoint}`;
          this.log(`Auth attempt failed at ${endpoint}:`, error.message);
        }
      }
      
      if (!tokenResponse) {
        throw new Error(`Failed to authenticate: ${errorMessage}`);
      }
      
      this.accessToken = tokenResponse.access_token;
      this.log('Authentication successful');
      return this.accessToken;
    } catch (error) {
      this.log('Authentication failed:', error.message);
      throw error;
    }
  }
  
  /**
   * Gets capability statement from the FHIR server
   * @returns {Promise<object>} - Capability statement
   */
  async getCapabilityStatement() {
    await this.ensureClient();
    try {
      this.log('Getting capability statement');
      return await this.client.request('metadata');
    } catch (error) {
      this.log('Failed to get capability statement:', error.message);
      throw error;
    }
  }
  
  /**
   * Ensures the FHIR client is initialized
   * @returns {Promise<object>} - FHIR client
   */
  async ensureClient() {
    if (!this.client) {
      return this.initialize();
    }
    return this.client;
  }
  
  /**
   * Search for patients
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Search results
   */
  async searchPatients(params = {}) {
    await this.ensureClient();
    try {
      this.log('Searching patients with params:', params);
      return await this.client.request(`Patient${this.formatQueryString(params)}`);
    } catch (error) {
      this.log('Patient search failed:', error.message);
      throw error;
    }
  }
  
  /**
   * Get a patient by ID
   * @param {string} id - Patient ID
   * @returns {Promise<Object>} - Patient resource
   */
  async getPatient(id) {
    await this.ensureClient();
    try {
      this.log(`Getting patient with ID: ${id}`);
      return await this.client.request(`Patient/${id}`);
    } catch (error) {
      this.log(`Failed to get patient ${id}:`, error.message);
      throw error;
    }
  }
  
  /**
   * Search for observations
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Search results
   */
  async searchObservations(params = {}) {
    await this.ensureClient();
    try {
      this.log('Searching observations with params:', params);
      return await this.client.request(`Observation${this.formatQueryString(params)}`);
    } catch (error) {
      this.log('Observation search failed:', error.message);
      throw error;
    }
  }
  
  /**
   * Get observations for a patient
   * @param {string} patientId - Patient ID
   * @param {Object} [additionalParams] - Additional search parameters
   * @returns {Promise<Object>} - Search results
   */
  async getPatientObservations(patientId, additionalParams = {}) {
    const params = { ...additionalParams, patient: patientId };
    return this.searchObservations(params);
  }
  
  /**
   * Search for conditions
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Search results
   */
  async searchConditions(params = {}) {
    await this.ensureClient();
    try {
      this.log('Searching conditions with params:', params);
      return await this.client.request(`Condition${this.formatQueryString(params)}`);
    } catch (error) {
      this.log('Condition search failed:', error.message);
      throw error;
    }
  }
  
  /**
   * Get conditions for a patient
   * @param {string} patientId - Patient ID
   * @param {Object} [additionalParams] - Additional search parameters
   * @returns {Promise<Object>} - Search results
   */
  async getPatientConditions(patientId, additionalParams = {}) {
    const params = { ...additionalParams, patient: patientId };
    return this.searchConditions(params);
  }
  
  /**
   * Formats query string from parameters object
   * @param {Object} params - Query parameters
   * @returns {string} - Formatted query string
   */
  formatQueryString(params) {
    if (!params || Object.keys(params).length === 0) {
      return '';
    }
    
    const queryParts = [];
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
      }
    }
    
    return queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  }
  
  /**
   * Make a direct FHIR request
   * @param {string} path - FHIR resource path
   * @param {Object} [params] - Query parameters
   * @returns {Promise<Object>} - Response data
   */
  async request(path, params = {}) {
    await this.ensureClient();
    try {
      this.log(`Making request to: ${path}`);
      return await this.client.request(`${path}${this.formatQueryString(params)}`);
    } catch (error) {
      this.log(`Request to ${path} failed:`, error.message);
      throw error;
    }
  }
}

module.exports = StandardFhirClient;
