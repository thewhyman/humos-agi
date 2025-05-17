#!/usr/bin/env python3
"""
FHIR Interactive Client
This client directly connects to a FHIR server to fetch patient data based on user input.
"""

import asyncio
import os
import json
from server import make_fhir_request, format_patient

class FHIRClient:
    def __init__(self):
        self.fhir_server = os.environ.get("FHIR_MCP_SERVER_URL", "https://hapi.fhir.org/baseR4")
        print(f"Using FHIR server: {self.fhir_server}")
    
    async def search_patients(self, name):
        """Search for patients by name"""
        url = f"{self.fhir_server}/Patient?name={name}&_count=5"
        result = await make_fhir_request(url)
        
        if not result or not result.get("entry"):
            return "No patients found matching your search criteria."
        
        patient_list = []
        for entry in result["entry"]:
            if "resource" in entry:
                patient = entry["resource"]
                patient_id = patient.get("id", "Unknown")
                patient_summary = format_patient(patient)
                patient_list.append(f"Patient ID: {patient_id}\n{patient_summary}")
        
        return "\n\n======\n\n".join(patient_list)
    
    async def get_patient(self, patient_id):
        """Get detailed information for a specific patient"""
        url = f"{self.fhir_server}/Patient/{patient_id}"
        data = await make_fhir_request(url)
        
        if not data:
            return "Unable to fetch patient information."
        
        return format_patient(data)
    
    async def get_observations(self, patient_id):
        """Get medical observations for a patient"""
        url = f"{self.fhir_server}/Observation?patient={patient_id}&_count=15&_sort=-date"
        data = await make_fhir_request(url)
        
        if not data or not data.get("entry"):
            return "No observations found for this patient."
        
        observations = []
        for entry in data["entry"]:
            if "resource" in entry:
                obs = entry["resource"]
                
                # Format observation
                code_display = "Unknown Test"
                if obs.get("code") and obs["code"].get("coding") and len(obs["code"]["coding"]) > 0:
                    code_display = obs["code"]["coding"][0].get("display", "Unknown Test")
                
                # Format value
                value = "No value recorded"
                if obs.get("valueQuantity"):
                    val = obs["valueQuantity"].get("value", "")
                    unit = obs["valueQuantity"].get("unit", "")
                    value = f"{val} {unit}"
                elif obs.get("valueCodeableConcept"):
                    if obs["valueCodeableConcept"].get("text"):
                        value = obs["valueCodeableConcept"]["text"]
                    elif obs["valueCodeableConcept"].get("coding") and len(obs["valueCodeableConcept"]["coding"]) > 0:
                        value = obs["valueCodeableConcept"]["coding"][0].get("display", "Unknown")
                elif obs.get("valueString"):
                    value = obs["valueString"]
                
                # Get date
                date = obs.get("effectiveDateTime", "Unknown Date")
                status = obs.get("status", "unknown")
                
                observations.append(f"{code_display}: {value} ({date}, {status})")
        
        if not observations:
            return "No valid observations found for this patient."
        
        return "\n---\n".join(observations)
    
    async def get_conditions(self, patient_id):
        """Get medical conditions for a patient"""
        url = f"{self.fhir_server}/Condition?patient={patient_id}&_count=20&_sort=-recorded-date"
        data = await make_fhir_request(url)
        
        if not data or not data.get("entry"):
            return "No conditions found for this patient."
        
        conditions = []
        for entry in data["entry"]:
            if "resource" in entry:
                condition = entry["resource"]
                
                # Get the condition name/code
                name = "Unknown Condition"
                if condition.get("code") and condition["code"].get("coding") and len(condition["code"]["coding"]) > 0:
                    name = condition["code"]["coding"][0].get("display", "Unknown Condition")
                elif condition.get("code") and condition["code"].get("text"):
                    name = condition["code"]["text"]
                
                # Get clinical status
                status = "unknown"
                if condition.get("clinicalStatus") and condition["clinicalStatus"].get("coding") and len(condition["clinicalStatus"]["coding"]) > 0:
                    status = condition["clinicalStatus"]["coding"][0].get("code", "unknown")
                
                # Get onset date if available
                onset = "Unknown onset"
                if condition.get("onsetDateTime"):
                    onset = condition["onsetDateTime"]
                
                conditions.append(f"{name} (Status: {status}, Onset: {onset})")
        
        if not conditions:
            return "No valid conditions found for this patient."
        
        return "\n---\n".join(conditions)
    
    async def get_medications(self, patient_id):
        """Get medications for a patient"""
        url = f"{self.fhir_server}/MedicationRequest?patient={patient_id}&_count=20&_sort=-authored"
        data = await make_fhir_request(url)
        
        if not data or not data.get("entry"):
            return "No medications found for this patient."
        
        medications = []
        for entry in data["entry"]:
            if "resource" in entry:
                med_request = entry["resource"]
                
                # Get medication name
                med_name = "Unknown Medication"
                if med_request.get("medicationCodeableConcept"):
                    if med_request["medicationCodeableConcept"].get("text"):
                        med_name = med_request["medicationCodeableConcept"]["text"]
                    elif med_request["medicationCodeableConcept"].get("coding") and len(med_request["medicationCodeableConcept"]["coding"]) > 0:
                        med_name = med_request["medicationCodeableConcept"]["coding"][0].get("display", "Unknown Medication")
                
                # Get dosage instructions
                dosage = "No dosage information"
                if med_request.get("dosageInstruction") and len(med_request["dosageInstruction"]) > 0:
                    dosage_obj = med_request["dosageInstruction"][0]
                    if dosage_obj.get("text"):
                        dosage = dosage_obj["text"]
                
                # Get status
                status = med_request.get("status", "unknown")
                
                # Get authorized date
                date = med_request.get("authoredOn", "Unknown date")
                
                medications.append(f"{med_name}\nDosage: {dosage}\nStatus: {status}\nAuthorized: {date}")
        
        if not medications:
            return "No valid medications found for this patient."
        
        return "\n---\n".join(medications)
    
    async def get_allergies(self, patient_id):
        """Get allergies for a patient"""
        url = f"{self.fhir_server}/AllergyIntolerance?patient={patient_id}&_count=10"
        data = await make_fhir_request(url)
        
        if not data or not data.get("entry"):
            return "No allergies found for this patient."
        
        allergies = []
        for entry in data["entry"]:
            if "resource" in entry:
                allergy = entry["resource"]
                
                # Get substance
                substance = "Unknown allergen"
                if allergy.get("code") and allergy["code"].get("coding") and len(allergy["code"]["coding"]) > 0:
                    substance = allergy["code"]["coding"][0].get("display", "Unknown allergen")
                elif allergy.get("code") and allergy["code"].get("text"):
                    substance = allergy["code"]["text"]
                
                # Get severity and manifestation
                severity = "Unknown severity"
                manifestation = "Unknown reaction"
                
                if allergy.get("reaction") and len(allergy["reaction"]) > 0:
                    reaction = allergy["reaction"][0]
                    severity = reaction.get("severity", "Unknown severity")
                    
                    if reaction.get("manifestation") and len(reaction["manifestation"]) > 0:
                        man = reaction["manifestation"][0]
                        if man.get("coding") and len(man["coding"]) > 0:
                            manifestation = man["coding"][0].get("display", "Unknown reaction")
                        elif man.get("text"):
                            manifestation = man["text"]
                
                allergies.append(f"Allergen: {substance}\nSeverity: {severity}\nManifestation: {manifestation}")
        
        if not allergies:
            return "No valid allergies found for this patient."
        
        return "\n---\n".join(allergies)
    
    async def collect_all_medical_data(self, patient_id):
        """Collect all medical data for a patient"""
        data = {}
        print(f"\nRetrieving complete medical record for Patient ID: {patient_id}")
        
        # Get all data in parallel for efficiency
        patient_task = asyncio.create_task(self.get_patient(patient_id))
        observations_task = asyncio.create_task(self.get_observations(patient_id))
        conditions_task = asyncio.create_task(self.get_conditions(patient_id))
        medications_task = asyncio.create_task(self.get_medications(patient_id))
        allergies_task = asyncio.create_task(self.get_allergies(patient_id))
        
        # Await all tasks
        data['patient'] = await patient_task
        data['observations'] = await observations_task
        data['conditions'] = await conditions_task
        data['medications'] = await medications_task
        data['allergies'] = await allergies_task
        
        return data
    
    def display_medical_data(self, data):
        """Display comprehensive medical data in a formatted way"""
        print("\n" + "="*60)
        print(" "*20 + "PATIENT MEDICAL RECORD")
        print("="*60)
        
        # Basic patient info
        print("\n📋 [PATIENT INFORMATION]")
        print(data['patient'])
        
        # Medical conditions
        print("\n" + "="*60)
        print("🏥 [MEDICAL CONDITIONS]")
        print(data['conditions'])
        
        # Medications
        print("\n" + "="*60)
        print("💊 [MEDICATIONS]")
        print(data['medications'])
        
        # Observations
        print("\n" + "="*60)
        print("🔬 [OBSERVATIONS]")
        print(data['observations'])
        
        # Allergies
        print("\n" + "="*60)
        print("⚠️ [ALLERGIES]")
        print(data['allergies'])
    
    async def run(self):
        """Run the interactive client"""
        print("="*60)
        print(" "*15 + "FHIR INTERACTIVE HEALTH RECORDS")
        print("="*60)
        print("\nThis application retrieves medical data for patients from a FHIR server.")
        
        while True:
            # Get patient name from user
            name = input("\nEnter patient name to search (or 'q' to quit): ")
            if name.lower() == 'q':
                print("Exiting application.")
                break
                
            if not name:
                print("Please enter a valid name.")
                continue
                
            try:
                # Search for patients with the provided name
                print(f"\nSearching for patients named '{name}'...")
                search_results = await self.search_patients(name)
                
                if "No patients found" in search_results:
                    print(f"No patients found with name '{name}'.")
                    print("Try a different name (common test names: 'Smith', 'Jones', 'Patient')")
                    continue
                
                print("\nSearch Results:")
                print(search_results)
                
                # Ask user to select a patient ID
                patient_id = input("\nEnter the Patient ID from the search results to view complete medical record: ")
                if not patient_id:
                    print("No Patient ID provided. Returning to search.")
                    continue
                
                # Collect all medical data for the selected patient
                try:
                    medical_data = await self.collect_all_medical_data(patient_id)
                    self.display_medical_data(medical_data)
                    
                    action = input("\nPress Enter to continue or 'q' to quit: ")
                    if action.lower() == 'q':
                        print("Exiting application.")
                        break
                        
                except Exception as e:
                    print(f"Error retrieving medical data: {str(e)}")
            
            except Exception as e:
                print(f"Error: {str(e)}")
                print("There was a problem connecting to the FHIR server.")
                break

if __name__ == "__main__":
    client = FHIRClient()
    asyncio.run(client.run())
