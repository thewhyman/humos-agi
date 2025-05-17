/**
 * HumOS AGI - Public FHIR Server Demo
 * 
 * This demo connects to a public FHIR server to demonstrate healthcare data
 * access capabilities without authentication barriers.
 */

const StandardFhirClient = require('./standard-fhir-client');
require('dotenv').config();

// Available public FHIR servers for testing
const PUBLIC_FHIR_SERVERS = [
  {
    name: 'HAPI FHIR R4',
    url: 'https://hapi.fhir.org/baseR4',
    version: 'R4'
  },
  {
    name: 'SMART Health IT',
    url: 'https://r4.smarthealthit.org',
    version: 'R4'
  },
  {
    name: 'Open Epic FHIR',
    url: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
    version: 'R4'
  }
];

/**
 * Formats a FHIR date for display
 * @param {string} date - FHIR date string
 * @returns {string} - Formatted date
 */
function formatDate(date) {
  if (!date) return 'Unknown';
  try {
    return new Date(date).toLocaleDateString();
  } catch (e) {
    return date;
  }
}

/**
 * Gets patient name from FHIR resource
 * @param {Object} patient - FHIR patient resource
 * @returns {string} - Formatted name
 */
function getPatientName(patient) {
  if (!patient || !patient.name || patient.name.length === 0) {
    return 'Unknown';
  }
  
  const name = patient.name[0];
  const given = name.given ? name.given.join(' ') : '';
  const family = name.family || '';
  
  return `${given} ${family}`.trim() || 'Unknown';
}

/**
 * Gets observation value from FHIR resource
 * @param {Object} observation - FHIR observation resource
 * @returns {string} - Formatted value
 */
function getObservationValue(observation) {
  if (observation.valueQuantity) {
    return `${observation.valueQuantity.value} ${observation.valueQuantity.unit || ''}`.trim();
  } else if (observation.valueCodeableConcept) {
    return observation.valueCodeableConcept.text || 
      (observation.valueCodeableConcept.coding?.[0]?.display || 'Unknown');
  } else if (observation.valueString) {
    return observation.valueString;
  } else if (observation.component) {
    // Handle multi-component observations (e.g., BP with systolic and diastolic)
    return observation.component
      .map(comp => {
        const name = comp.code?.text || comp.code?.coding?.[0]?.display || 'Component';
        let value = 'Unknown';
        if (comp.valueQuantity) {
          value = `${comp.valueQuantity.value} ${comp.valueQuantity.unit || ''}`.trim();
        }
        return `${name}: ${value}`;
      })
      .join(', ');
  }
  
  return 'No value recorded';
}

/**
 * Run the FHIR demo
 */
async function runDemo() {
  console.log('HumOS AGI - Public FHIR Server Demo');
  console.log('===================================\n');
  
  // Use the first public FHIR server
  const server = PUBLIC_FHIR_SERVERS[0];
  console.log(`Using public FHIR server: ${server.name} (${server.url})`);
  
  try {
    // Initialize client
    const client = new StandardFhirClient({
      baseUrl: server.url,
      debug: true
    });
    
    // Step 1: Initialize client
    console.log('\n========== Step 1: Get server metadata ==========');
    try {
      await client.initialize();
      const metadata = await client.getCapabilityStatement();
      
      console.log('Server Information:');
      console.log(`- Name: ${metadata.software?.name || 'Unknown'}`);
      console.log(`- Version: ${metadata.software?.version || 'Unknown'}`);
      console.log(`- FHIR Version: ${metadata.fhirVersion || 'Unknown'}`);
      
      // List supported resources
      const resources = metadata.rest?.[0]?.resource || [];
      console.log(`- Supported Resources: ${resources.length}`);
      resources.slice(0, 5).forEach(res => {
        console.log(`  * ${res.type}: ${res.interaction?.map(i => i.code).join(', ') || 'read-only'}`);
      });
    } catch (error) {
      console.log('Failed to get metadata:', error.message);
      console.log('Continuing with direct resource access...');
    }
    
    // Step 2: Find some patients
    console.log('\n========== Step 2: Search for patients ==========');
    try {
      console.log('Searching for patients...');
      const patients = await client.searchPatients({ _count: 5 });
      
      console.log(`Found ${patients.total || patients.entry?.length || 0} patients`);
      
      if (patients.entry && patients.entry.length > 0) {
        console.log('\nSample patients:');
        
        // Display sample patient information
        for (let i = 0; i < Math.min(3, patients.entry.length); i++) {
          const patient = patients.entry[i].resource;
          console.log(`\nPatient #${i+1}:`);
          console.log(`- ID: ${patient.id}`);
          console.log(`- Name: ${getPatientName(patient)}`);
          console.log(`- Gender: ${patient.gender || 'Unknown'}`);
          console.log(`- Birth Date: ${formatDate(patient.birthDate)}`);
          
          // Save the first patient ID for further exploration
          if (i === 0) {
            firstPatientId = patient.id;
          }
        }
        
        // Continue with first patient
        const firstPatient = patients.entry[0].resource;
        const patientId = firstPatient.id;
        const patientName = getPatientName(firstPatient);
        
        // Step 3: Get patient's observations
        console.log(`\n========== Step 3: Get observations for ${patientName} ==========`);
        try {
          console.log(`Fetching observations for patient ${patientId}...`);
          const observations = await client.getPatientObservations(patientId, { _count: 10 });
          
          console.log(`Found ${observations.total || observations.entry?.length || 0} observations`);
          
          if (observations.entry && observations.entry.length > 0) {
            console.log('\nSample observations:');
            
            // Group observations by type for better display
            const obsTypes = {};
            
            observations.entry.forEach(entry => {
              const obs = entry.resource;
              const code = obs.code?.coding?.[0]?.display || obs.code?.text || 'Unknown';
              
              if (!obsTypes[code]) {
                obsTypes[code] = [];
              }
              
              obsTypes[code].push({
                date: obs.effectiveDateTime || obs.issued,
                value: getObservationValue(obs),
                status: obs.status
              });
            });
            
            // Display by type
            Object.entries(obsTypes).slice(0, 5).forEach(([type, values]) => {
              console.log(`\n${type}:`);
              values.slice(0, 3).forEach((v, i) => {
                console.log(`  ${i+1}. ${v.value} (${formatDate(v.date)}) [${v.status}]`);
              });
            });
          }
        } catch (error) {
          console.log('Failed to get observations:', error.message);
        }
        
        // Step 4: Get patient's conditions
        console.log(`\n========== Step 4: Get conditions for ${patientName} ==========`);
        try {
          console.log(`Fetching conditions for patient ${patientId}...`);
          const conditions = await client.getPatientConditions(patientId, { _count: 10 });
          
          console.log(`Found ${conditions.total || conditions.entry?.length || 0} conditions`);
          
          if (conditions.entry && conditions.entry.length > 0) {
            console.log('\nSample conditions:');
            conditions.entry.slice(0, 5).forEach((entry, i) => {
              const condition = entry.resource;
              const code = condition.code?.coding?.[0]?.display || condition.code?.text || 'Unknown';
              const status = condition.clinicalStatus?.coding?.[0]?.code || 'unknown';
              const onset = formatDate(condition.onsetDateTime);
              
              console.log(`${i+1}. ${code} (${status}) - Onset: ${onset}`);
            });
          }
        } catch (error) {
          console.log('Failed to get conditions:', error.message);
        }
        
        // Step 5: More resource types (demonstrate comprehensive healthcare data)
        console.log(`\n========== Step 5: Additional healthcare data for ${patientName} ==========`);
        
        // Try to get immunizations
        try {
          console.log('\nFetching immunizations...');
          const immunizations = await client.request(`Immunization?patient=${patientId}&_count=5`);
          
          console.log(`Found ${immunizations.total || immunizations.entry?.length || 0} immunizations`);
          
          if (immunizations.entry && immunizations.entry.length > 0) {
            console.log('\nSample immunizations:');
            immunizations.entry.slice(0, 3).forEach((entry, i) => {
              const imm = entry.resource;
              const vaccine = imm.vaccineCode?.coding?.[0]?.display || imm.vaccineCode?.text || 'Unknown vaccine';
              const date = formatDate(imm.occurrenceDateTime);
              const status = imm.status;
              
              console.log(`${i+1}. ${vaccine} (${date}) - Status: ${status}`);
            });
          }
        } catch (error) {
          console.log('Could not fetch immunizations:', error.message);
        }
        
        // Try to get medications
        try {
          console.log('\nFetching medications...');
          const medications = await client.request(`MedicationRequest?patient=${patientId}&_count=5`);
          
          console.log(`Found ${medications.total || medications.entry?.length || 0} medication requests`);
          
          if (medications.entry && medications.entry.length > 0) {
            console.log('\nSample medications:');
            medications.entry.slice(0, 3).forEach((entry, i) => {
              const med = entry.resource;
              const medication = med.medicationCodeableConcept?.coding?.[0]?.display || 
                                med.medicationCodeableConcept?.text || 'Unknown medication';
              const status = med.status;
              
              console.log(`${i+1}. ${medication} - Status: ${status}`);
            });
          }
        } catch (error) {
          console.log('Could not fetch medications:', error.message);
        }
      }
    } catch (error) {
      console.log('Failed to search patients:', error.message);
    }
    
    console.log('\nDemo completed successfully.');
    
  } catch (error) {
    console.error('Demo failed with error:', error.message);
  }
}

// Run the demo
runDemo().catch(error => {
  console.error('Unhandled error:', error);
});
