from typing import Any, Dict, List, Optional
import os
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("fhir")

# FHIR Server configurations
DEFAULT_FHIR_SERVER = "https://hapi.fhir.org/baseR4"
USER_AGENT = "humos-fhir-client/1.0"

# Get FHIR server URL from environment or use default
FHIR_SERVER = os.environ.get("FHIR_MCP_SERVER_URL", DEFAULT_FHIR_SERVER)

async def make_fhir_request(url: str) -> Dict[str, Any] | None:
    """Make a request to a FHIR server"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/fhir+json"
    }
    
    # Add authorization if available
    api_key = os.environ.get("FLEXPA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"FHIR request error: {e}")
            return None

def format_observation(observation: Dict[str, Any]) -> str:
    """Format an observation for display"""
    code_display = "Unknown Test"
    if observation.get("code") and observation["code"].get("coding") and len(observation["code"]["coding"]) > 0:
        code_display = observation["code"]["coding"][0].get("display", "Unknown Test")
    
    # Format the value based on observation type
    value = "No value recorded"
    if observation.get("valueQuantity"):
        val = observation["valueQuantity"].get("value", "")
        unit = observation["valueQuantity"].get("unit", "")
        value = f"{val} {unit}"
    elif observation.get("valueCodeableConcept"):
        if observation["valueCodeableConcept"].get("text"):
            value = observation["valueCodeableConcept"]["text"]
        elif observation["valueCodeableConcept"].get("coding") and len(observation["valueCodeableConcept"]["coding"]) > 0:
            value = observation["valueCodeableConcept"]["coding"][0].get("display", "Unknown")
    elif observation.get("valueString"):
        value = observation["valueString"]
    
    # Get date of observation
    date = observation.get("effectiveDateTime", "Unknown Date")
    status = observation.get("status", "unknown")
    
    return f"{code_display}: {value} ({date}, {status})"

def format_patient(patient: Dict[str, Any]) -> str:
    """Format patient information for display"""
    if not patient:
        return "Patient information not available"
    
    # Extract name
    name = "Unknown"
    if patient.get("name") and len(patient["name"]) > 0:
        name_obj = patient["name"][0]
        given = " ".join(name_obj.get("given", [])) if name_obj.get("given") else ""
        family = name_obj.get("family", "")
        name = f"{given} {family}".strip()
    
    # Extract other demographics
    gender = patient.get("gender", "Unknown")
    birth_date = patient.get("birthDate", "Unknown")
    
    # Address
    address = "No address on file"
    if patient.get("address") and len(patient["address"]) > 0:
        addr = patient["address"][0]
        line = ", ".join(addr.get("line", [])) if addr.get("line") else ""
        city = addr.get("city", "")
        state = addr.get("state", "")
        postal_code = addr.get("postalCode", "")
        address = f"{line}, {city}, {state} {postal_code}".strip().replace(", ,", ",")
    
    return f"""Name: {name}
Gender: {gender}
Birth Date: {birth_date}
Address: {address}"""

@mcp.tool()
async def get_patient(patient_id: str) -> str:
    """Get patient information by ID."""

    url = f"{FHIR_SERVER}/Patient/{patient_id}"
    data = await make_fhir_request(url)

    if not data:
        return "Unable to fetch patient information."
    
    return format_patient(data)

@mcp.tool()
async def get_observations(patient_id: str, count: int = 10) -> str:
    """Get medical observations for a patient."""
    
    url = f"{FHIR_SERVER}/Observation?patient={patient_id}&_count={count}&_sort=-date"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No observations found for this patient."

    observations = []
    for entry in data["entry"]:
        if "resource" in entry:
            obs = entry["resource"]
            observations.append(format_observation(obs))
    
    if not observations:
        return "No valid observations found for this patient."
    
    return "\n---\n".join(observations)

@mcp.tool()
async def get_conditions(patient_id: str) -> str:
    """Get medical conditions (problems) for a patient."""
    
    url = f"{FHIR_SERVER}/Condition?patient={patient_id}&_count=20&_sort=-recorded-date"
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

@mcp.tool()
async def get_medications(patient_id: str) -> str:
    """Get medications for a patient."""
    
    url = f"{FHIR_SERVER}/MedicationRequest?patient={patient_id}&_count=20&_sort=-authored"
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

@mcp.tool()
async def search_patients(name: str = "", identifier: str = "") -> str:
    """Search for patients by name or identifier."""
    
    params = []
    if name:
        params.append(f"name={name}")
    if identifier:
        params.append(f"identifier={identifier}")
    
    if not params:
        return "Please provide a name or identifier to search for patients."
    
    query_string = "&".join(params) + "&_count=5"
    url = f"{FHIR_SERVER}/Patient?{query_string}"
    
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No patients found matching your search criteria."

    patients_summary = []
    for entry in data["entry"]:
        if "resource" in entry:
            patient = entry["resource"]
            patient_summary = format_patient(patient)
            patients_summary.append(f"Patient ID: {patient.get('id', 'Unknown')}\n{patient_summary}")
    
    if not patients_summary:
        return "No valid patient records found matching your search criteria."
    
    return "\n\n======\n\n".join(patients_summary)

@mcp.tool()
async def get_allergies(patient_id: str) -> str:
    """Get allergies for a patient."""
    
    url = f"{FHIR_SERVER}/AllergyIntolerance?patient={patient_id}&_count=10"
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
            
            # Get severity and manifestation if available
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

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')