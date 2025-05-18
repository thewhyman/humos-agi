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

# Enable mock data mode (for testing without an actual FHIR server)
# Default is True (use mock data), set USE_MOCK_DATA=False to use real FHIR server
USE_MOCK_DATA = os.environ.get("USE_MOCK_DATA", "True").lower() in ["true", "1", "t", "yes"]

# Mock data for common FHIR resources
# Mock medications data
MOCK_MEDICATIONS = {
    "default": [
        {
            "medicationCodeableConcept": {"coding": [{"display": "Lisinopril 10 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet once daily"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Metformin 500 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet twice daily with meals"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Simvastatin 20 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet at bedtime"}],
            "status": "active"
        }
    ],
    "1": [
        {
            "medicationCodeableConcept": {"coding": [{"display": "Albuterol 90 mcg/actuation inhaler"}]},
            "dosageInstruction": [{"text": "2 puffs every 4-6 hours as needed for shortness of breath"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Fluticasone 110 mcg/actuation inhaler"}]},
            "dosageInstruction": [{"text": "2 puffs twice daily"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Loratadine 10 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily as needed for allergies"}],
            "status": "active"
        }
    ],
    "2": [
        {
            "medicationCodeableConcept": {"coding": [{"display": "Warfarin 5 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily as directed by provider"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Furosemide 40 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily in the morning"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Metoprolol succinate 50 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Allopurinol 300 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily"}],
            "status": "active"
        }
    ],
    "3": [
        {
            "medicationCodeableConcept": {"coding": [{"display": "Sumatriptan 50 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet at onset of migraine, may repeat after 2 hours if needed"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Dicyclomine 10 mg oral capsule"}]},
            "dosageInstruction": [{"text": "1 capsule four times daily before meals and at bedtime"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Sertraline 50 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily in the morning"}],
            "status": "completed"
        }
    ],
    "4": [
        {
            "medicationCodeableConcept": {"coding": [{"display": "Tiotropium 18 mcg inhalation capsule"}]},
            "dosageInstruction": [{"text": "Inhale contents of 1 capsule daily using HandiHaler device"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Alendronate 70 mg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet once weekly on empty stomach with water, remain upright for 30 minutes"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Levothyroxine 75 mcg oral tablet"}]},
            "dosageInstruction": [{"text": "1 tablet daily in the morning on empty stomach"}],
            "status": "active"
        },
        {
            "medicationCodeableConcept": {"coding": [{"display": "Gabapentin 300 mg oral capsule"}]},
            "dosageInstruction": [{"text": "1 capsule three times daily"}],
            "status": "active"
        }
    ]
}

# Mock patient data
MOCK_PATIENTS = {
    "default": {
        "id": "default",
        "name": [{"use": "official", "family": "Smith", "given": ["John", "Edward"]}],
        "gender": "male",
        "birthDate": "1974-12-25",
        "address": [{"use": "home", "line": ["123 Main St"], "city": "Anytown", "state": "CA", "postalCode": "12345"}],
        "telecom": [
            {"system": "phone", "value": "555-555-5555", "use": "home"},
            {"system": "email", "value": "john.smith@example.com"}
        ],
        "communication": [{"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en", "display": "English"}]}}],
        "maritalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "M", "display": "Married"}]},
        "active": True
    },
    "1": {
        "id": "1",
        "name": [{"use": "official", "family": "Johnson", "given": ["Emily", "Rose"]}],
        "gender": "female",
        "birthDate": "1985-04-19",
        "address": [{"use": "home", "line": ["456 Oak Avenue"], "city": "Springfield", "state": "IL", "postalCode": "62704"}],
        "telecom": [
            {"system": "phone", "value": "555-123-4567", "use": "home"},
            {"system": "email", "value": "emily.johnson@example.com"}
        ],
        "communication": [{"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en", "display": "English"}]}}],
        "maritalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "S", "display": "Single"}]},
        "active": True
    },
    "2": {
        "id": "2",
        "name": [{"use": "official", "family": "Williams", "given": ["Robert", "James"]}],
        "gender": "male",
        "birthDate": "1952-08-10",
        "address": [{"use": "home", "line": ["789 Elm Street"], "city": "Riverdale", "state": "NY", "postalCode": "10471"}],
        "telecom": [
            {"system": "phone", "value": "555-987-6543", "use": "home"},
            {"system": "email", "value": "robert.williams@example.com"}
        ],
        "communication": [{"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en", "display": "English"}]}}],
        "maritalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "M", "display": "Married"}]},
        "active": True
    },
    "3": {
        "id": "3",
        "name": [{"use": "official", "family": "Garcia", "given": ["Maria", "Elena"]}],
        "gender": "female",
        "birthDate": "1990-11-27",
        "address": [{"use": "home", "line": ["321 Pine Road"], "city": "Portland", "state": "OR", "postalCode": "97205"}],
        "telecom": [
            {"system": "phone", "value": "555-456-7890", "use": "mobile"},
            {"system": "email", "value": "maria.garcia@example.com"}
        ],
        "communication": [
            {"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en", "display": "English"}]}},
            {"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "es", "display": "Spanish"}]}}
        ],
        "maritalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "S", "display": "Single"}]},
        "active": True
    },
    "4": {
        "id": "4",
        "name": [{"use": "official", "family": "Chen", "given": ["Li"]}],
        "gender": "female",
        "birthDate": "1945-06-15",
        "address": [{"use": "home", "line": ["555 Maple Court"], "city": "Chicago", "state": "IL", "postalCode": "60601"}],
        "telecom": [
            {"system": "phone", "value": "555-789-0123", "use": "home"},
            {"system": "email", "value": "li.chen@example.com"}
        ],
        "communication": [
            {"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en", "display": "English"}]}},
            {"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "zh", "display": "Chinese"}]}}
        ],
        "maritalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "W", "display": "Widowed"}]},
        "active": True
    }
}

# Mock allergies data
MOCK_ALLERGIES = {
    "default": [
        {
            "code": {"coding": [{"display": "Penicillin"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Hives"}]}]}],
            "criticality": "high",
            "verificationStatus": "confirmed"
        },
        {
            "code": {"coding": [{"display": "Shellfish"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Anaphylaxis"}]}]}],
            "criticality": "high",
            "verificationStatus": "confirmed"
        }
    ],
    "1": [
        {
            "code": {"coding": [{"display": "Pollen"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Allergic rhinitis"}]}]}],
            "criticality": "low",
            "verificationStatus": "confirmed"
        },
        {
            "code": {"coding": [{"display": "Dust mites"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Wheezing"}]}]}],
            "criticality": "moderate",
            "verificationStatus": "confirmed"
        },
        {
            "code": {"coding": [{"display": "Pet dander"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Asthma attack"}]}]}],
            "criticality": "high",
            "verificationStatus": "confirmed"
        }
    ],
    "2": [
        {
            "code": {"coding": [{"display": "Sulfa drugs"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Rash"}]}]}],
            "criticality": "moderate",
            "verificationStatus": "confirmed"
        },
        {
            "code": {"coding": [{"display": "NSAIDs"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Angioedema"}]}]}],
            "criticality": "high",
            "verificationStatus": "confirmed"
        }
    ],
    "3": [
        {
            "code": {"coding": [{"display": "Latex"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Contact dermatitis"}]}]}],
            "criticality": "moderate",
            "verificationStatus": "confirmed"
        }
    ],
    "4": [
        {
            "code": {"coding": [{"display": "Contrast dye"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Itching"}]}]}],
            "criticality": "moderate",
            "verificationStatus": "confirmed"
        },
        {
            "code": {"coding": [{"display": "Aspirin"}]},
            "reaction": [{"manifestation": [{"coding": [{"display": "Bronchospasm"}]}]}],
            "criticality": "high",
            "verificationStatus": "confirmed"
        }
    ]
}

# Mock observations data with vital signs
MOCK_OBSERVATIONS = {
    "default": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 72, "unit": "beats/minute"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
            "valueQuantity": {"value": 132, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
            "valueQuantity": {"value": 82, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "valueQuantity": {"value": 37.2, "unit": "Cel"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "29463-7", "display": "Body weight"}]},
            "valueQuantity": {"value": 70.3, "unit": "kg"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "39156-5", "display": "BMI"}]},
            "valueQuantity": {"value": 24.3, "unit": "kg/m2"},
            "effectiveDateTime": "2024-05-01T10:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "18262-6", "display": "Cholesterol in LDL"}]},
            "valueQuantity": {"value": 128, "unit": "mg/dL"},
            "effectiveDateTime": "2024-04-15T09:00:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "2339-0", "display": "Glucose"}]},
            "valueQuantity": {"value": 95, "unit": "mg/dL"},
            "effectiveDateTime": "2024-04-15T09:00:00Z",
            "status": "final"
        }
    ],
    "1": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 82, "unit": "beats/minute"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
            "valueQuantity": {"value": 122, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
            "valueQuantity": {"value": 76, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "valueQuantity": {"value": 36.8, "unit": "Cel"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "33536-4", "display": "Exhaled CO2"}]},
            "valueQuantity": {"value": 4.8, "unit": "%"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "20564-1", "display": "Oxygen saturation in Blood"}]},
            "valueQuantity": {"value": 97, "unit": "%"},
            "effectiveDateTime": "2024-05-02T14:15:00Z",
            "status": "final"
        }
    ],
    "2": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 68, "unit": "beats/minute"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
            "valueQuantity": {"value": 145, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
            "valueQuantity": {"value": 92, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "valueQuantity": {"value": 36.4, "unit": "Cel"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "32693-4", "display": "Creatinine"}]},
            "valueQuantity": {"value": 1.8, "unit": "mg/dL"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "2160-0", "display": "Creatinine clearance"}]},
            "valueQuantity": {"value": 48, "unit": "mL/min"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "Hemoglobin A1c"}]},
            "valueQuantity": {"value": 6.8, "unit": "%"},
            "effectiveDateTime": "2024-05-03T11:45:00Z",
            "status": "final"
        }
    ],
    "3": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 78, "unit": "beats/minute"},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
            "valueQuantity": {"value": 118, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
            "valueQuantity": {"value": 74, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "valueQuantity": {"value": 37.1, "unit": "Cel"},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "2345-7", "display": "Glucose"}]},
            "valueQuantity": {"value": 85, "unit": "mg/dL"},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "35209-6", "display": "Anxiety assessment"}]},
            "valueCodeableConcept": {"coding": [{"code": "LA6568-5", "display": "Moderate"}]},
            "effectiveDateTime": "2024-05-04T09:30:00Z",
            "status": "final"
        }
    ],
    "4": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": 84, "unit": "beats/minute"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
            "valueQuantity": {"value": 138, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
            "valueQuantity": {"value": 88, "unit": "mmHg"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
            "valueQuantity": {"value": 36.9, "unit": "Cel"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "19926-5", "display": "FEV1"}]},
            "valueQuantity": {"value": 1.8, "unit": "L"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "20564-1", "display": "Oxygen saturation"}]},
            "valueQuantity": {"value": 93, "unit": "%"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "69434-4", "display": "Bone mineral density"}]},
            "valueQuantity": {"value": -2.3, "unit": "score"},
            "effectiveDateTime": "2024-05-05T15:40:00Z",
            "status": "final"
        }
    ]
}

# Mock conditions data
MOCK_CONDITIONS = {
    "default": [
        {
            "code": {"coding": [{"display": "Essential hypertension"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2020-03-15"
        },
        {
            "code": {"coding": [{"display": "Type 2 diabetes mellitus"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2018-11-05"
        },
        {
            "code": {"coding": [{"display": "Hyperlipidemia"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2019-05-22"
        },
        {
            "code": {"coding": [{"display": "Osteoarthritis of knee"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2021-07-18"
        },
        {
            "code": {"coding": [{"display": "Gastroesophageal reflux disease"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2017-09-30"
        }
    ],
    "1": [
        {
            "code": {"coding": [{"display": "Asthma"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2010-02-15"
        },
        {
            "code": {"coding": [{"display": "Seasonal allergic rhinitis"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2012-04-10"
        },
        {
            "code": {"coding": [{"display": "Anxiety disorder"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2019-11-23"
        }
    ],
    "2": [
        {
            "code": {"coding": [{"display": "Coronary artery disease"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2015-08-20"
        },
        {
            "code": {"coding": [{"display": "Chronic kidney disease"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2018-03-12"
        },
        {
            "code": {"coding": [{"display": "Atrial fibrillation"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2017-06-30"
        },
        {
            "code": {"coding": [{"display": "Gout"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2020-01-15"
        }
    ],
    "3": [
        {
            "code": {"coding": [{"display": "Migraine with aura"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2018-05-12"
        },
        {
            "code": {"coding": [{"display": "Irritable bowel syndrome"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2016-11-28"
        },
        {
            "code": {"text": "Major depressive disorder, recurrent"},
            "clinicalStatus": {"coding": [{"code": "resolved"}]},
            "onsetDateTime": "2015-02-15"
        }
    ],
    "4": [
        {
            "code": {"coding": [{"display": "Chronic obstructive pulmonary disease"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2014-09-05"
        },
        {
            "code": {"coding": [{"display": "Osteoporosis"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2019-03-12"
        },
        {
            "code": {"coding": [{"display": "Hypothyroidism"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2016-07-25"
        },
        {
            "code": {"coding": [{"display": "Chronic pain syndrome"}]},
            "clinicalStatus": {"coding": [{"code": "active"}]},
            "onsetDateTime": "2017-11-18"
        }
    ]
}

# Mock search patients results
MOCK_PATIENT_SEARCH = {
    "default": [
        MOCK_PATIENTS["1"],
        MOCK_PATIENTS["2"],
        MOCK_PATIENTS["3"],
        MOCK_PATIENTS["4"]
    ],
    "john": [
        {
            "id": "1",
            "name": [{"use": "official", "family": "Doe", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1990-01-01",
            "address": [{"use": "home", "line": ["123 Main St"], "city": "Anytown", "state": "CA", "postalCode": "12345"}]
        },
        {
            "id": "2",
            "name": [{"use": "official", "family": "Smith", "given": ["John", "Robert"]}],
            "gender": "male",
            "birthDate": "1985-03-15"
        }
    ],
    "emily": [
        {
            "id": "1",
            "name": [{"use": "official", "family": "Johnson", "given": ["Emily", "Rose"]}],
            "gender": "female",
            "birthDate": "1985-04-19"
        }
    ],
    "maria": [
        {
            "id": "3",
            "name": [{"use": "official", "family": "Garcia", "given": ["Maria", "Elena"]}],
            "gender": "female",
            "birthDate": "1990-11-27"
        }
    ],
    "li": [
        {
            "id": "4",
            "name": [{"use": "official", "family": "Chen", "given": ["Li"]}],
            "gender": "female",
            "birthDate": "1945-06-15"
        }
    ]
}

def normalize_patient_id(patient_id: str) -> str:
    """Normalize patient ID to ensure consistency across the system.
    
    This handles legacy formats like 'Patient1' and standardizes them to numeric IDs.
    """
    # Convert to string if it's not already
    patient_id_str = str(patient_id)
    
    # Handle legacy formats
    if patient_id_str.startswith("Patient"):
        # Extract the numeric part from 'PatientX'
        return patient_id_str.replace("Patient", "")
    elif patient_id_str.startswith("pat"):
        # Convert 'pat2' to '2'
        return patient_id_str.replace("pat", "")
    
    # Return the normalized ID
    return patient_id_str

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
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except Exception as e:
            print(f"Error making FHIR request: {e}")
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
    """Get detailed information for a specific patient."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for patient (id: {normalized_id})")
        
        # Check if we have this specific patient in our mock data
        if normalized_id in MOCK_PATIENTS:
            return format_patient(MOCK_PATIENTS[normalized_id])
        
        # Return default patient as fallback
        print("Requested patient not found in mock data, using default patient")
        return format_patient(MOCK_PATIENTS["default"])
    
    # Use real FHIR server
    url = f"{FHIR_SERVER}/Patient/{normalized_id}"
    data = await make_fhir_request(url)

    if not data:
        return "Unable to fetch patient information."
    
    return format_patient(data)

@mcp.tool()
async def get_observations(patient_id: str, count: int = 10) -> str:
    """Get medical observations for a patient."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for observations (patient_id: {normalized_id})")        
        
        # Get patient-specific observations or use default
        mock_patient_observations = MOCK_OBSERVATIONS.get(normalized_id, MOCK_OBSERVATIONS["default"])
        
        # Limit to requested count
        limited_observations = mock_patient_observations[:count] if count < len(mock_patient_observations) else mock_patient_observations
        
        observations = []
        for obs in limited_observations:
            # Format the observation the same way as real data
            observations.append(format_observation(obs))
        
        if not observations:
            return "No valid observations found for this patient."
        
        return "\n---\n".join(observations)
    
    # Use real FHIR server
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
    """Get medical conditions for a patient."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for conditions (patient_id: {normalized_id})")
        
        # Get patient-specific conditions or use default
        mock_patient_conditions = MOCK_CONDITIONS.get(normalized_id, MOCK_CONDITIONS["default"])
        
        conditions = []
        for condition in mock_patient_conditions:
            # Get the condition display name
            name = "Unknown Condition"
            if condition.get("code") and condition["code"].get("coding") and len(condition["code"]["coding"]) > 0:
                name = condition["code"]["coding"][0].get("display", "Unknown Condition")
            
            # Get the condition status
            status = "unknown"
            if condition.get("clinicalStatus") and condition["clinicalStatus"].get("coding") and len(condition["clinicalStatus"]["coding"]) > 0:
                status = condition["clinicalStatus"]["coding"][0].get("code", "unknown")
            
            # Get the onset date
            onset = condition.get("onsetDateTime", "Unknown date")
            
            # Format the condition
            conditions.append(f"{name} (Status: {status}, Onset: {onset})")
        
        if not conditions:
            return "No conditions found for this patient."
        
        return "\n---\n".join(conditions)
    
    # Use real FHIR server
    url = f"{FHIR_SERVER}/Condition?patient={normalized_id}&_count=20&_sort=-recorded-date"
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
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for medications (patient_id: {normalized_id})")
        
        # Get patient-specific medications or use default
        mock_patient_medications = MOCK_MEDICATIONS.get(normalized_id, MOCK_MEDICATIONS["default"])
        
        medications = []
        for med in mock_patient_medications:
            # Get the medication name
            name = "Unknown Medication"
            if med.get("medicationCodeableConcept") and med["medicationCodeableConcept"].get("coding") and len(med["medicationCodeableConcept"]["coding"]) > 0:
                name = med["medicationCodeableConcept"]["coding"][0].get("display", "Unknown Medication")
            
            # Get the medication status
            status = med.get("status", "unknown")
            
            # Get the dosage instructions
            dosage = "No dosage information"
            if med.get("dosageInstruction") and len(med["dosageInstruction"]) > 0 and med["dosageInstruction"][0].get("text"):
                dosage = med["dosageInstruction"][0]["text"]
            
            # Format the medication
            medications.append(f"{name} (Status: {status}, Dosage: {dosage})")
        
        if not medications:
            return "No medications found for this patient."
        
        return "\n---\n".join(medications)
    
    # Use real FHIR server
    url = f"{FHIR_SERVER}/MedicationRequest?patient={normalized_id}&_count=15&_sort=-authored"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No medications found for this patient."

    medications = []
    for entry in data["entry"]:
        if "resource" in entry:
            med_request = entry["resource"]
            
            # Get medication name
            name = "Unknown Medication"
            if med_request.get("medicationCodeableConcept") and med_request["medicationCodeableConcept"].get("coding") and len(med_request["medicationCodeableConcept"]["coding"]) > 0:
                name = med_request["medicationCodeableConcept"]["coding"][0].get("display", "Unknown Medication")
            elif med_request.get("medicationCodeableConcept") and med_request["medicationCodeableConcept"].get("text"):
                name = med_request["medicationCodeableConcept"]["text"]
            
            # Get dosage information if available
            dosage = "No dosage information"
            if med_request.get("dosageInstruction") and len(med_request["dosageInstruction"]) > 0:
                if med_request["dosageInstruction"][0].get("text"):
                    dosage = med_request["dosageInstruction"][0]["text"]
            
            # Get status
            status = med_request.get("status", "unknown")
            
            medications.append(f"{name} (Dosage: {dosage}, Status: {status})")
    
    if not medications:
        return "No valid medications found for this patient."
    
    return "\n---\n".join(medications)

@mcp.tool()
async def search_patients(name: str = "", identifier: str = "") -> str:
    """Search for patients by name or identifier."""
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for patient search (name: {name}, identifier: {identifier})")
        
        # Normalize search parameters to lowercase for case-insensitive matching
        search_name = name.lower() if name else ""
        
        # Get patients matching search term or use default
        matching_patients = []
        
        # Search by name if provided
        if search_name:
            # Check if we have an exact match for the name in our mock data
            if search_name in MOCK_PATIENT_SEARCH:
                matching_patients = MOCK_PATIENT_SEARCH[search_name]
            else:
                # Otherwise, search through all patient names
                for patient_id, patient_data in MOCK_PATIENTS.items():
                    if patient_id != "default":
                        # Check if search term is in any part of the patient name
                        patient_name = ""
                        if patient_data.get("name") and len(patient_data["name"]) > 0:
                            name_obj = patient_data["name"][0]
                            if name_obj.get("family"):
                                patient_name += name_obj["family"].lower() + " "
                            if name_obj.get("given"):
                                patient_name += " ".join(name_obj["given"]).lower()
                        
                        if search_name in patient_name:
                            matching_patients.append(patient_data)
        
        # Search by identifier if provided
        if identifier and not matching_patients:
            # Simply check if an ID matches the identifier
            if identifier in MOCK_PATIENTS:
                matching_patients = [MOCK_PATIENTS[identifier]]
        
        # If no matches, use default set
        if not matching_patients:
            matching_patients = MOCK_PATIENT_SEARCH["default"][:5]  # Limit to 5 results
        
        # Format patient summaries
        patients_summary = []
        for patient in matching_patients:
            patient_summary = format_patient(patient)
            # Ensure consistent ID format - use the new numeric format
            patient_id = patient.get("id", "Unknown")
            # Remove any "Patient" prefix if it exists (for backward compatibility)
            if patient_id.startswith("Patient"):
                patient_id = patient_id.replace("Patient", "")
            patients_summary.append(f"Patient ID: {patient_id}\n{patient_summary}")
        
        if not patients_summary:
            return "No patients found matching your search criteria."
        
        return "\n\n======\n\n".join(patients_summary)
    
    # Use real FHIR server
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
            # Ensure consistent ID format
            patient_id = patient.get('id', 'Unknown')
            # Remove any "Patient" prefix if it exists (for backward compatibility)
            if patient_id.startswith("Patient"):
                patient_id = patient_id.replace("Patient", "")
            patients_summary.append(f"Patient ID: {patient_id}\n{patient_summary}")
    
    if not patients_summary:
        return "No valid patient records found matching your search criteria."
    
    return "\n\n======\n\n".join(patients_summary)

@mcp.tool()
async def get_allergies(patient_id: str) -> str:
    """Get allergies for a patient."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        print(f"Using mock data for allergies (patient_id: {normalized_id})")
        
        # Get patient-specific allergies or use default
        mock_patient_allergies = MOCK_ALLERGIES.get(normalized_id, MOCK_ALLERGIES["default"])
        
        allergies = []
        for allergy in mock_patient_allergies:
            # Get the allergen name
            name = "Unknown Allergen"
            if allergy.get("code") and allergy["code"].get("coding") and len(allergy["code"]["coding"]) > 0:
                name = allergy["code"]["coding"][0].get("display", "Unknown Allergen")
            
            # Get the reaction
            reaction = "Unknown reaction"
            if allergy.get("reaction") and len(allergy["reaction"]) > 0 and allergy["reaction"][0].get("manifestation") and len(allergy["reaction"][0]["manifestation"]) > 0:
                if allergy["reaction"][0]["manifestation"][0].get("coding") and len(allergy["reaction"][0]["manifestation"][0]["coding"]) > 0:
                    reaction = allergy["reaction"][0]["manifestation"][0]["coding"][0].get("display", "Unknown reaction")
            
            # Get the criticality
            criticality = allergy.get("criticality", "unknown")
            
            # Format the allergy
            allergies.append(f"{name} (Reaction: {reaction}, Criticality: {criticality})")
        
        if not allergies:
            return "No valid allergies found for this patient."
        
        return "\n---\n".join(allergies)
    
    # Use real FHIR server
    url = f"{FHIR_SERVER}/AllergyIntolerance?patient={patient_id}&_count=15"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No allergies found for this patient."

    allergies = []
    for entry in data["entry"]:
        if "resource" in entry:
            allergy = entry["resource"]
            
            # Get the allergy name/substance
            name = "Unknown Allergen"
            if allergy.get("code") and allergy["code"].get("coding") and len(allergy["code"]["coding"]) > 0:
                name = allergy["code"]["coding"][0].get("display", "Unknown Allergen")
            elif allergy.get("code") and allergy["code"].get("text"):
                name = allergy["code"]["text"]
            
            # Get reaction if available
            reaction = "Unknown reaction"
            if allergy.get("reaction") and len(allergy["reaction"]) > 0:
                if allergy["reaction"][0].get("manifestation") and len(allergy["reaction"][0]["manifestation"]) > 0:
                    if allergy["reaction"][0]["manifestation"][0].get("coding") and len(allergy["reaction"][0]["manifestation"][0]["coding"]) > 0:
                        reaction = allergy["reaction"][0]["manifestation"][0]["coding"][0].get("display", "Unknown reaction")
                    elif allergy["reaction"][0]["manifestation"][0].get("text"):
                        reaction = allergy["reaction"][0]["manifestation"][0]["text"]
            
            # Get criticality if available
            criticality = "unknown"
            if allergy.get("criticality"):
                criticality = allergy["criticality"]
            
            allergies.append(f"{name} (Reaction: {reaction}, Criticality: {criticality})")
    
    if not allergies:
        return "No valid allergies found for this patient."
    
    return "\n---\n".join(allergies)

@mcp.tool()
async def get_procedures(patient_id: str) -> str:
    """Get medical procedures for a patient."""
    
    url = f"{FHIR_SERVER}/Procedure?patient={patient_id}&_count=20&_sort=-date"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No procedures found for this patient."

    procedures = []
    for entry in data["entry"]:
        if "resource" in entry:
            procedure = entry["resource"]
            
            # Get the procedure name/code
            name = "Unknown Procedure"
            if procedure.get("code") and procedure["code"].get("coding") and len(procedure["code"]["coding"]) > 0:
                name = procedure["code"]["coding"][0].get("display", "Unknown Procedure")
            elif procedure.get("code") and procedure["code"].get("text"):
                name = procedure["code"]["text"]
            
            # Get status
            status = procedure.get("status", "unknown")
            
            # Get procedure date
            date = "Unknown date"
            if procedure.get("performedDateTime"):
                date = procedure["performedDateTime"]
            elif procedure.get("performedPeriod") and procedure["performedPeriod"].get("start"):
                date = procedure["performedPeriod"]["start"]
            
            # Get performer
            performer = "Unknown performer"
            if procedure.get("performer") and len(procedure["performer"]) > 0:
                performer_detail = procedure["performer"][0]
                if performer_detail.get("actor") and performer_detail["actor"].get("display"):
                    performer = performer_detail["actor"]["display"]
            
            procedures.append(f"{name}\nDate: {date}\nStatus: {status}\nPerformer: {performer}")
    
    if not procedures:
        return "No valid procedures found for this patient."
    
    return "\n---\n".join(procedures)

@mcp.tool()
async def get_immunizations(patient_id: str) -> str:
    """Get immunization records for a patient."""
    
    url = f"{FHIR_SERVER}/Immunization?patient={patient_id}&_count=20"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No immunizations found for this patient."

    immunizations = []
    for entry in data["entry"]:
        if "resource" in entry:
            imm = entry["resource"]
            
            # Get vaccine name
            vaccine = "Unknown vaccine"
            if imm.get("vaccineCode") and imm["vaccineCode"].get("coding") and len(imm["vaccineCode"]["coding"]) > 0:
                vaccine = imm["vaccineCode"]["coding"][0].get("display", "Unknown vaccine")
            elif imm.get("vaccineCode") and imm["vaccineCode"].get("text"):
                vaccine = imm["vaccineCode"]["text"]
            
            # Get date
            date = "Unknown date"
            if imm.get("occurrenceDateTime"):
                date = imm["occurrenceDateTime"]
            
            # Get status
            status = imm.get("status", "unknown")
            
            # Get dose
            dose = "Dose information not available"
            if imm.get("doseQuantity"):
                value = imm["doseQuantity"].get("value", "")
                unit = imm["doseQuantity"].get("unit", "")
                dose = f"{value} {unit}".strip()
            
            immunizations.append(f"{vaccine}\nDate: {date}\nStatus: {status}\nDose: {dose}")
    
    if not immunizations:
        return "No valid immunizations found for this patient."
    
    return "\n---\n".join(immunizations)

@mcp.tool()
async def get_diagnostic_reports(patient_id: str) -> str:
    """Get diagnostic reports for a patient."""
    
    url = f"{FHIR_SERVER}/DiagnosticReport?patient={patient_id}&_count=20&_sort=-date"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No diagnostic reports found for this patient."

    reports = []
    for entry in data["entry"]:
        if "resource" in entry:
            report = entry["resource"]
            
            # Get report name/type
            report_type = "Unknown report"
            if report.get("code") and report["code"].get("coding") and len(report["code"]["coding"]) > 0:
                report_type = report["code"]["coding"][0].get("display", "Unknown report")
            elif report.get("code") and report["code"].get("text"):
                report_type = report["code"]["text"]
            
            # Get status
            status = report.get("status", "unknown")
            
            # Get issued date
            date = "Unknown date"
            if report.get("effectiveDateTime"):
                date = report["effectiveDateTime"]
            elif report.get("issued"):
                date = report["issued"]
            
            # Get conclusion
            conclusion = report.get("conclusion", "No conclusion provided")
            
            reports.append(f"{report_type}\nDate: {date}\nStatus: {status}\nConclusion: {conclusion}")
    
    if not reports:
        return "No valid diagnostic reports found for this patient."
    
    return "\n---\n".join(reports)

@mcp.tool()
async def get_care_plans(patient_id: str) -> str:
    """Get care plans for a patient."""
    
    url = f"{FHIR_SERVER}/CarePlan?patient={patient_id}&_count=20&_sort=-date"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No care plans found for this patient."

    care_plans = []
    for entry in data["entry"]:
        if "resource" in entry:
            plan = entry["resource"]
            
            # Get title
            title = plan.get("title", "Untitled Care Plan")
            
            # Get status
            status = plan.get("status", "unknown")
            
            # Get period
            period = "No time period specified"
            if plan.get("period"):
                start = plan["period"].get("start", "unknown start")
                end = plan["period"].get("end", "ongoing")
                period = f"From {start} to {end}"
            
            # Get goals
            goals = []
            if plan.get("goal") and len(plan["goal"]) > 0:
                for goal_ref in plan["goal"]:
                    if goal_ref.get("display"):
                        goals.append(goal_ref["display"])
            
            goals_text = "No specific goals documented."
            if goals:
                goals_text = ", ".join(goals)
            
            care_plans.append(f"{title}\nStatus: {status}\nPeriod: {period}\nGoals: {goals_text}")
    
    if not care_plans:
        return "No valid care plans found for this patient."
    
    return "\n---\n".join(care_plans)

@mcp.tool()
async def get_vitals(patient_id: str) -> str:
    """Get vital signs for a patient."""
    
    # LOINC codes for common vital signs
    vital_codes = [
        "8867-4",  # Heart rate
        "8480-6",  # Blood pressure systolic
        "8462-4",  # Blood pressure diastolic
        "8310-5",  # Body temperature
        "9279-1",  # Respiratory rate
        "8302-2",  # Body height
        "29463-7", # Body weight
        "39156-5", # BMI
        "59408-5"   # Oxygen saturation
    ]
    
    code_filter = "|".join(vital_codes)
    url = f"{FHIR_SERVER}/Observation?patient={patient_id}&code={code_filter}&_count=50&_sort=-date"
    data = await make_fhir_request(url)

    if not data or not data.get("entry"):
        return "No vital signs found for this patient."

    vitals = []
    seen_codes = set()  # To track the most recent value for each vital type
    
    for entry in data["entry"]:
        if "resource" in entry:
            vital = entry["resource"]
            
            # Get the vital sign type
            code = ""
            if vital.get("code") and vital["code"].get("coding") and len(vital["code"]["coding"]) > 0:
                code = vital["code"]["coding"][0].get("code", "")
                name = vital["code"]["coding"][0].get("display", "Unknown Vital")
            else:
                continue  # Skip if we can't identify the vital sign
            
            # Skip if we've already seen this vital type (we're sorted by date, so first one is most recent)
            if code in seen_codes:
                continue
            
            seen_codes.add(code)
            
            # Format the value
            value = "No value recorded"
            if vital.get("valueQuantity"):
                val = vital["valueQuantity"].get("value", "")
                unit = vital["valueQuantity"].get("unit", "")
                value = f"{val} {unit}"
            elif vital.get("component") and code in ["8480-6", "8462-4"]:  # Handle BP components
                components = []
                for comp in vital["component"]:
                    if comp.get("code") and comp["code"].get("coding") and comp.get("valueQuantity"):
                        comp_name = comp["code"]["coding"][0].get("display", "")
                        comp_val = comp["valueQuantity"].get("value", "")
                        comp_unit = comp["valueQuantity"].get("unit", "")
                        components.append(f"{comp_name}: {comp_val} {comp_unit}")
                if components:
                    value = ", ".join(components)
            
            # Get date
            date = vital.get("effectiveDateTime", "Unknown Date")
            
            vitals.append(f"{name}: {value} ({date})")
    
    if not vitals:
        return "No valid vital signs found for this patient."
    
    return "\n---\n".join(vitals)

@mcp.tool()
async def get_patient_summary(patient_id: str) -> str:
    """Get a comprehensive medical summary for a patient."""
    
    tasks = [
        ("patient", get_patient(patient_id)),
        ("conditions", get_conditions(patient_id)),
        ("medications", get_medications(patient_id)),
        ("allergies", get_allergies(patient_id)),
        ("observations", get_observations(patient_id, 10)),
        ("vitals", get_vitals(patient_id)),
        ("immunizations", get_immunizations(patient_id)),
        ("procedures", get_procedures(patient_id))
    ]
    
    results = {}
    for name, task in tasks:
        try:
            results[name] = await task
        except Exception as e:
            results[name] = f"Error retrieving {name}: {str(e)}"
    
    summary = [
        "=== PATIENT MEDICAL SUMMARY ===",
        "",
        "## PATIENT INFORMATION",
        results["patient"],
        "",
        "## VITAL SIGNS",
        results["vitals"],
        "",
        "## MEDICAL CONDITIONS",
        results["conditions"],
        "",
        "## MEDICATIONS",
        results["medications"],
        "",
        "## ALLERGIES",
        results["allergies"],
        "",
        "## IMMUNIZATIONS",
        results["immunizations"],
        "",
        "## PROCEDURES",
        results["procedures"],
        "",
        "## RECENT OBSERVATIONS",
        results["observations"],
        "",
        "=== END OF SUMMARY ==="
    ]
    
    return "\n".join(summary)

@mcp.tool()
async def get_all_medical_data(patient_id: str) -> dict:
    """Get all available medical data for a patient as a structured dictionary."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    tasks = [
        ("patient", get_patient(normalized_id)),
        ("conditions", get_conditions(normalized_id)),
        ("medications", get_medications(normalized_id)),
        ("allergies", get_allergies(normalized_id)),
        ("observations", get_observations(normalized_id, 15)),
        ("vitals", get_vitals(normalized_id)),
        ("immunizations", get_immunizations(normalized_id)),
        ("procedures", get_procedures(normalized_id)),
        ("diagnosticReports", get_diagnostic_reports(normalized_id)),
        ("carePlans", get_care_plans(normalized_id))
    ]
    
    results = {}
    for name, task in tasks:
        try:
            results[name] = await task
        except Exception as e:
            results[name] = f"Error retrieving {name}: {str(e)}"
    
    return results

@mcp.tool()
async def get_health_recommendations(patient_id: str) -> str:
    """Generate personalized health recommendations based on a patient's medical data."""
    # Normalize the patient ID for consistent behavior
    normalized_id = normalize_patient_id(patient_id)
    
    # First, get all the patient's medical data to create a comprehensive profile
    medical_data = await get_all_medical_data(normalized_id)
    
    # Format data for the recommendation engine
    formatted_data = []
    
    # Add patient info
    if medical_data.get("patient"):
        formatted_data.append(f"Patient Information: {medical_data['patient']}")
    
    # Add conditions
    if medical_data.get("conditions"):
        formatted_data.append(f"Medical Conditions: {medical_data['conditions']}")
    
    # Add medications
    if medical_data.get("medications"):
        formatted_data.append(f"Current Medications: {medical_data['medications']}")
    
    # Add allergies
    if medical_data.get("allergies"):
        formatted_data.append(f"Allergies: {medical_data['allergies']}")
    
    # Add observations (lab results and vitals)
    if medical_data.get("observations"):
        formatted_data.append(f"Observations: {medical_data['observations']}")
    
    # Create a comprehensive medical profile for the LLM
    medical_profile = "\n\n".join(formatted_data)
    
    # Prepare the prompt for the LLM
    system_prompt = """You are a healthcare assistant with expertise in preventive care and health management. 
    Based on the patient's medical profile, provide personalized health recommendations. 
    Focus on evidence-based suggestions for:
    1. Lifestyle modifications appropriate for their conditions
    2. Dietary considerations based on their health status
    3. Exercise recommendations considering their physical condition
    4. Medication adherence tips if applicable
    5. Preventive screenings they should consider based on their age, gender, and risk factors
    6. Mental health considerations if relevant
    
    Format your response in a clear, actionable manner. Do not diagnose new conditions or suggest medication changes.
    Make your recommendations specific to this patient's actual conditions, not generic health advice.
    Cite reasons for each recommendation based on the patient's specific health data."""
    
    user_prompt = f"""Here is the patient's medical profile:
    
    {medical_profile}
    
    Based on this information, what personalized health recommendations would you suggest for this patient?"""
    
    # Create the messages for the LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Use the perplexity-ask MCP to generate recommendations
        from mcp.registry import get_tool
        
        perplexity_ask = get_tool("perplexity_ask")
        if perplexity_ask:
            response = await perplexity_ask(messages=messages)
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                return "Unable to generate health recommendations: Invalid response format."
        else:
            # Fallback if perplexity_ask isn't available
            return "Health recommendations feature requires the perplexity-ask MCP server."
    except Exception as e:
        # Provide a helpful error message with fallback recommendations
        print(f"Error generating health recommendations: {str(e)}")
        
        # Generate basic recommendations based on conditions
        conditions_list = medical_data.get("conditions", "No conditions found.")
        medications_list = medical_data.get("medications", "No medications found.")
        
        recommendations = ["Based on your medical profile, consider these general recommendations:"]
        recommendations.append("\n1. Regular follow-ups with your healthcare provider for all your conditions")
        recommendations.append("2. Maintain a balanced diet rich in fruits, vegetables, and whole grains")
        recommendations.append("3. Stay physically active as appropriate for your condition")
        recommendations.append("4. Take medications as prescribed")
        recommendations.append("5. Monitor your symptoms and report any changes to your provider")
        
        if "hypertension" in str(conditions_list).lower() or "blood pressure" in str(conditions_list).lower():
            recommendations.append("6. Consider blood pressure monitoring at home")
            recommendations.append("7. Reduce sodium intake")
        
        if "diabetes" in str(conditions_list).lower():
            recommendations.append("6. Regular blood glucose monitoring")
            recommendations.append("7. Be mindful of carbohydrate intake")
        
        if "asthma" in str(conditions_list).lower() or "copd" in str(conditions_list).lower():
            recommendations.append("6. Avoid known respiratory triggers")
            recommendations.append("7. Keep rescue inhalers accessible")
        
        # Add disclaimer
        recommendations.append("\nNOTE: These are general recommendations. Please consult with your healthcare provider for personalized medical advice.")
        
        return "\n".join(recommendations)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')