#!/usr/bin/env python3
"""
Interactive FHIR MCP Client
This client interacts with the FHIR MCP server to fetch patient data based on user input.
"""

import asyncio
import json
from mcp.client import Client

class FHIRInteractiveClient:
    def __init__(self):
        self.client = Client("fhir")
        self.patient_id = None
    
    async def search_patient(self, name):
        """Search for a patient by name"""
        print(f"\nSearching for patients named '{name}'...")
        result = await self.client.search_patients(name=name)
        return result
    
    async def get_patient_details(self, patient_id):
        """Get detailed information for a specific patient"""
        print(f"\nFetching details for Patient ID: {patient_id}")
        return await self.client.get_patient(patient_id=patient_id)
    
    async def get_observations(self, patient_id):
        """Get medical observations for a patient"""
        print(f"\nFetching observations for Patient ID: {patient_id}")
        return await self.client.get_observations(patient_id=patient_id, count=15)
    
    async def get_conditions(self, patient_id):
        """Get medical conditions for a patient"""
        print(f"\nFetching medical conditions for Patient ID: {patient_id}")
        return await self.client.get_conditions(patient_id=patient_id)
    
    async def get_medications(self, patient_id):
        """Get medications for a patient"""
        print(f"\nFetching medications for Patient ID: {patient_id}")
        return await self.client.get_medications(patient_id=patient_id)
    
    async def get_allergies(self, patient_id):
        """Get allergies for a patient"""
        print(f"\nFetching allergies for Patient ID: {patient_id}")
        return await self.client.get_allergies(patient_id=patient_id)
    
    async def collect_all_medical_data(self, patient_id):
        """Collect all medical data for a patient"""
        data = {}
        data['patient'] = await self.get_patient_details(patient_id)
        data['observations'] = await self.get_observations(patient_id)
        data['conditions'] = await self.get_conditions(patient_id)
        data['medications'] = await self.get_medications(patient_id)
        data['allergies'] = await self.get_allergies(patient_id)
        return data
    
    async def display_medical_data(self, data):
        """Display comprehensive medical data in a formatted way"""
        print("\n" + "="*50)
        print("COMPREHENSIVE PATIENT MEDICAL RECORD")
        print("="*50)
        
        # Basic patient info
        print("\n[PATIENT INFORMATION]")
        print(data['patient'])
        
        # Medical conditions
        print("\n" + "="*50)
        print("[MEDICAL CONDITIONS]")
        print(data['conditions'])
        
        # Medications
        print("\n" + "="*50)
        print("[MEDICATIONS]")
        print(data['medications'])
        
        # Observations
        print("\n" + "="*50)
        print("[OBSERVATIONS]")
        print(data['observations'])
        
        # Allergies
        print("\n" + "="*50)
        print("[ALLERGIES]")
        print(data['allergies'])
    
    async def run(self):
        """Run the interactive client"""
        print("="*50)
        print("FHIR INTERACTIVE HEALTH RECORDS CLIENT")
        print("="*50)
        print("\nThis client will search for patients by name and retrieve their medical data.")
        
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
                search_results = await self.search_patient(name)
                
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
                
                # Collect and display all medical data for the selected patient
                try:
                    medical_data = await self.collect_all_medical_data(patient_id)
                    await self.display_medical_data(medical_data)
                    
                    action = input("\nPress Enter to continue or 'q' to quit: ")
                    if action.lower() == 'q':
                        print("Exiting application.")
                        break
                        
                except Exception as e:
                    print(f"Error retrieving medical data: {str(e)}")
            
            except Exception as e:
                print(f"Error: {str(e)}")
                print("There was a problem connecting to the FHIR server.")
                print("Make sure the MCP server is running.")
                break

if __name__ == "__main__":
    client = FHIRInteractiveClient()
    asyncio.run(client.run())
