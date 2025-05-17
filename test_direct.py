#!/usr/bin/env python3
"""
Simple direct test for FHIR functionality
This doesn't rely on the MCP protocol but directly tests our FHIR implementation
"""

import asyncio
import os
import json
from server import make_fhir_request, format_patient

async def test_fhir_direct():
    print("===== Direct FHIR API Test =====\n")
    
    # Default FHIR test server
    fhir_server = os.environ.get("FHIR_MCP_SERVER_URL", "https://hapi.fhir.org/baseR4")
    print(f"Using FHIR server: {fhir_server}")
    
    # Test with a standard test patient ID
    patient_id = "example"
    patient_url = f"{fhir_server}/Patient/{patient_id}"
    
    print(f"\nFetching patient with ID: {patient_id}")
    patient_data = await make_fhir_request(patient_url)
    
    if patient_data:
        print("\nPatient found!")
        formatted_patient = format_patient(patient_data)
        print(formatted_patient)
    else:
        print("\nFailed to retrieve patient data.")
        print("Let's try another common test patient ID...")
        
        # Try another common test patient ID
        patient_id = "pat1"
        patient_url = f"{fhir_server}/Patient/{patient_id}"
        print(f"\nFetching patient with ID: {patient_id}")
        patient_data = await make_fhir_request(patient_url)
        
        if patient_data:
            print("\nPatient found!")
            formatted_patient = format_patient(patient_data)
            print(formatted_patient)
        else:
            print("\nFailed to retrieve patient data.")
            
            # Let's try searching instead
            print("\nSearching for patients with name 'Smith'")
            search_url = f"{fhir_server}/Patient?name=Smith&_count=3"
            search_results = await make_fhir_request(search_url)
            
            if search_results and search_results.get("entry"):
                print(f"Found {len(search_results['entry'])} patients!")
                for entry in search_results["entry"]:
                    if "resource" in entry:
                        patient = entry["resource"]
                        patient_id = patient.get("id", "Unknown")
                        print(f"\nPatient ID: {patient_id}")
                        print(format_patient(patient))
            else:
                print("No patients found or search failed.")

if __name__ == "__main__":
    asyncio.run(test_fhir_direct())
