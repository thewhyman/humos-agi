/**
 * HumOS AGI - FHIR Integration Demo
 * 
 * This demo shows how to connect to a public FHIR server and access
 * healthcare data using FHIR standards. It demonstrates the core
 * functionality of the HumOS healthcare data platform.
 */

const SimpleFhirClient = require('./simple-fhir-client');
require('dotenv').config();

// Available public FHIR servers
const PUBLIC_SERVERS = [
  {
    name: 'HAPI FHIR (R4)',
    url: 'https://hapi.fhir.org/baseR4',
    version: 'R4',
    requiresAuth: false
  },
  {
    name: 'SMART Health IT',
    url: 'https://r4.smarthealthit.org',
    version: 'R4',
    requiresAuth: false
  }
];

/**
 * Format a FHIR date for display
 */
function formatDate(dateString) {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return dateString;
  }
}

/**
 * Get formatted patient name
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
 * Get formatted observation value
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
  console.log('HumOS AGI - FHIR Integration Demo');
  console.log('================================\n');
  
  // Use the first public server (HAPI FHIR)
  const server = PUBLIC_SERVERS[0];
  console.log(`Using FHIR server: ${server.name}`);
  console.log(`URL: ${server.url}`);
  console.log(`FHIR Version: ${server.version}`);
  console.log('');
  
  try {
    // Create FHIR client
    const client = new SimpleFhirClient({
      baseUrl: server.url,
      debug: true
    });
    
    // Step 1: Get server metadata
    console.log('========== Step 1: Server Metadata ==========');
    try {
      const metadata = await client.getCapabilityStatement();
      
      console.log('Server Information:');
      console.log(`- Software: ${metadata.software?.name || 'Unknown'} ${metadata.software?.version || ''}`);
      console.log(`- FHIR Version: ${metadata.fhirVersion}`);
      
      const resources = metadata.rest?.[0]?.resource || [];
      console.log(`- Supported Resources: ${resources.length}`);
      console.log('  Sample resources:');
      resources.slice(0, 5).forEach(resource => {
        console.log(`  * ${resource.type}`);
      });
    } catch (error) {
      console.log(`Error getting metadata: ${error.message}`);
      console.log('Continuing with available operations...');
    }
    
    // Step 2: Find patients
    console.log('\n========== Step 2: Patient Search ==========');
    const patients = await client.searchPatients({ _count: 5 });
    
    console.log(`Found ${patients.total || 'multiple'} patients`);
    console.log(`Received ${patients.entry?.length || 0} patients in this page`);
    
    if (!patients.entry || patients.entry.length === 0) {
      console.log('No patients found. Demo cannot continue.');
      return;
    }
    
    // Display sample patients
    console.log('\nSample patients:');
    for (let i = 0; i < Math.min(3, patients.entry.length); i++) {
      const patient = patients.entry[i].resource;
      console.log(`\nPatient #${i+1}:`);
      console.log(`- ID: ${patient.id}`);
      console.log(`- Name: ${getPatientName(patient)}`);
      console.log(`- Gender: ${patient.gender || 'Unknown'}`);
      console.log(`- Birth Date: ${formatDate(patient.birthDate)}`);
      console.log(`- Address: ${patient.address?.[0]?.city || 'Unknown'}, ${patient.address?.[0]?.state || ''}`);
    }
    
    // Get the first patient for detailed exploration
    const firstPatient = patients.entry[0].resource;
    const patientId = firstPatient.id;
    const patientName = getPatientName(firstPatient);
    
    // Step 3: Get patient observations
    console.log(`\n========== Step 3: Clinical Observations for ${patientName} ==========`);
    try {
      const observations = await client.getPatientObservations(patientId, { _count: 10 });
      
      console.log(`Found ${observations.total || observations.entry?.length || 0} observations`);
      
      if (observations.entry && observations.entry.length > 0) {
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
        console.log('\nObservations by Type:');
        Object.entries(obsTypes).slice(0, 5).forEach(([type, values]) => {
          console.log(`\n${type}:`);
          values.slice(0, 3).forEach((v, i) => {
            console.log(`  ${i+1}. ${v.value} (${formatDate(v.date)}) [${v.status}]`);
          });
        });
      }
    } catch (error) {
      console.log(`Error getting observations: ${error.message}`);
    }
    
    // Step 4: Get patient conditions
    console.log(`\n========== Step 4: Medical Conditions for ${patientName} ==========`);
    try {
      const conditions = await client.getPatientConditions(patientId, { _count: 10 });
      
      console.log(`Found ${conditions.total || conditions.entry?.length || 0} conditions`);
      
      if (conditions.entry && conditions.entry.length > 0) {
        console.log('\nActive Conditions:');
        const activeConditions = conditions.entry.filter(
          e => e.resource.clinicalStatus?.coding?.[0]?.code === 'active'
        );
        
        if (activeConditions.length > 0) {
          activeConditions.slice(0, 5).forEach((entry, i) => {
            const condition = entry.resource;
            const code = condition.code?.coding?.[0]?.display || condition.code?.text || 'Unknown';
            const category = condition.category?.[0]?.coding?.[0]?.display || 'General';
            const onset = formatDate(condition.onsetDateTime);
            
            console.log(`${i+1}. ${code}`);
            console.log(`   Category: ${category}`);
            console.log(`   Onset: ${onset}`);
          });
        } else {
          console.log('No active conditions found.');
        }
        
        console.log('\nResolved Conditions:');
        const resolvedConditions = conditions.entry.filter(
          e => e.resource.clinicalStatus?.coding?.[0]?.code === 'resolved'
        );
        
        if (resolvedConditions.length > 0) {
          resolvedConditions.slice(0, 3).forEach((entry, i) => {
            const condition = entry.resource;
            const code = condition.code?.coding?.[0]?.display || condition.code?.text || 'Unknown';
            console.log(`${i+1}. ${code} (resolved on ${formatDate(condition.abatementDateTime)})`);
          });
        } else {
          console.log('No resolved conditions found.');
        }
      }
    } catch (error) {
      console.log(`Error getting conditions: ${error.message}`);
    }
    
    // Step 5: Get additional healthcare data
    console.log(`\n========== Step 5: Additional Health Data for ${patientName} ==========`);
    
    // Get medications
    try {
      console.log('\nMedications:');
      const medications = await client.request(`MedicationRequest?patient=${patientId}&_count=5`);
      
      console.log(`Found ${medications.total || medications.entry?.length || 0} medication requests`);
      
      if (medications.entry && medications.entry.length > 0) {
        medications.entry.slice(0, 3).forEach((entry, i) => {
          const med = entry.resource;
          const medication = med.medicationCodeableConcept?.coding?.[0]?.display || 
                           med.medicationCodeableConcept?.text || 'Unknown medication';
          const status = med.status;
          const dosage = med.dosageInstruction?.[0]?.text || 'No dosage information';
          
          console.log(`${i+1}. ${medication}`);
          console.log(`   Status: ${status}`);
          console.log(`   Dosage: ${dosage}`);
        });
      }
    } catch (error) {
      console.log(`Error getting medications: ${error.message}`);
    }
    
    // Get allergies
    try {
      console.log('\nAllergies:');
      const allergies = await client.request(`AllergyIntolerance?patient=${patientId}&_count=5`);
      
      console.log(`Found ${allergies.total || allergies.entry?.length || 0} allergies`);
      
      if (allergies.entry && allergies.entry.length > 0) {
        allergies.entry.slice(0, 3).forEach((entry, i) => {
          const allergy = entry.resource;
          const substance = allergy.code?.coding?.[0]?.display || allergy.code?.text || 'Unknown allergen';
          const severity = allergy.reaction?.[0]?.severity || 'Unknown severity';
          const manifestation = allergy.reaction?.[0]?.manifestation?.[0]?.coding?.[0]?.display || 'Unknown reaction';
          
          console.log(`${i+1}. ${substance}`);
          console.log(`   Severity: ${severity}`);
          console.log(`   Manifestation: ${manifestation}`);
        });
      }
    } catch (error) {
      console.log(`Error getting allergies: ${error.message}`);
    }
    
    // Get immunizations
    try {
      console.log('\nImmunizations:');
      const immunizations = await client.request(`Immunization?patient=${patientId}&_count=5`);
      
      console.log(`Found ${immunizations.total || immunizations.entry?.length || 0} immunizations`);
      
      if (immunizations.entry && immunizations.entry.length > 0) {
        immunizations.entry.slice(0, 3).forEach((entry, i) => {
          const imm = entry.resource;
          const vaccine = imm.vaccineCode?.coding?.[0]?.display || imm.vaccineCode?.text || 'Unknown vaccine';
          const date = formatDate(imm.occurrenceDateTime);
          const status = imm.status;
          
          console.log(`${i+1}. ${vaccine}`);
          console.log(`   Date: ${date}`);
          console.log(`   Status: ${status}`);
        });
      }
    } catch (error) {
      console.log(`Error getting immunizations: ${error.message}`);
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
