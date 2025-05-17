/**
 * HumOS AGI - Simple FHIR Client
 * 
 * A lightweight FHIR client that works with public FHIR servers without authentication.
 * This enables demonstrating healthcare data integration capabilities quickly.
 */

const axios = require('axios');

class SimpleFhirClient {
  /**
   * Creates a new FHIR client
   * @param {Object} config - Configuration options
   * @param {string} config.baseUrl - Base URL of the FHIR server
   * @param {boolean} [config.debug=false] - Enable debug logging
   */
  constructor(config) {
    this.baseUrl = config.baseUrl;
    this.debug = config.debug || false;
    
    // Initialize HTTP client
    this.http = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000,
      headers: {
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json'
      }
    });
    
    this.log('Simple FHIR Client initialized');
    this.log(`Base URL: ${this.baseUrl}`);
  }
  
  /**
   * Log debug messages
   * @param {...any} args - Arguments to log
   */
  log(...args) {
    if (this.debug) {
      console.log('[FHIR Client]', ...args);
    }
  }
  
  /**
   * Makes a request to the FHIR server
   * @param {string} path - Resource path
   * @param {Object} [params] - Query parameters
   * @returns {Promise<Object>} - FHIR response
   */
  async request(path, params = {}) {
    try {
      this.log(`Requesting: ${path}`);
      
      // Add query parameters to URL if provided
      let url = path;
      if (Object.keys(params).length > 0) {
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(params)) {
          queryParams.append(key, value);
        }
        url = `${path}?${queryParams.toString()}`;
      }
      
      const response = await this.http.get(url);
      
      this.log(`Response status: ${response.status}`);
      return response.data;
    } catch (error) {
      this.log(`Error requesting ${path}:`, error.message);
      throw error;
    }
  }
  
  /**
   * Get server metadata (CapabilityStatement)
   * @returns {Promise<Object>} - FHIR CapabilityStatement
   */
  async getCapabilityStatement() {
    return this.request('metadata');
  }
  
  /**
   * Search for patients
   * @param {Object} params - Search parameters 
   * @returns {Promise<Object>} - Bundle of Patient resources
   */
  async searchPatients(params = {}) {
    return this.request('Patient', params);
  }
  
  /**
   * Get a specific patient by ID
   * @param {string} id - Patient ID 
   * @returns {Promise<Object>} - Patient resource
   */
  async getPatient(id) {
    return this.request(`Patient/${id}`);
  }
  
  /**
   * Search for observations
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Bundle of Observation resources
   */
  async searchObservations(params = {}) {
    return this.request('Observation', params);
  }
  
  /**
   * Get observations for a specific patient
   * @param {string} patientId - Patient ID
   * @param {Object} [additionalParams] - Additional search parameters
   * @returns {Promise<Object>} - Bundle of Observation resources
   */
  async getPatientObservations(patientId, additionalParams = {}) {
    const params = { ...additionalParams, patient: patientId };
    return this.searchObservations(params);
  }
  
  /**
   * Search for conditions
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Bundle of Condition resources
   */
  async searchConditions(params = {}) {
    return this.request('Condition', params);
  }
  
  /**
   * Get conditions for a specific patient
   * @param {string} patientId - Patient ID
   * @param {Object} [additionalParams] - Additional search parameters
   * @returns {Promise<Object>} - Bundle of Condition resources
   */
  async getPatientConditions(patientId, additionalParams = {}) {
    const params = { ...additionalParams, patient: patientId };
    return this.searchConditions(params);
  }
  
  /**
   * Search for medications
   * @param {Object} params - Search parameters
   * @returns {Promise<Object>} - Bundle of MedicationRequest resources
   */
  async searchMedications(params = {}) {
    return this.request('MedicationRequest', params);
  }
  
  /**
   * Get medications for a specific patient
   * @param {string} patientId - Patient ID
   * @param {Object} [additionalParams] - Additional search parameters
   * @returns {Promise<Object>} - Bundle of MedicationRequest resources
   */
  async getPatientMedications(patientId, additionalParams = {}) {
    const params = { ...additionalParams, patient: patientId };
    return this.searchMedications(params);
  }
}

module.exports = SimpleFhirClient;
