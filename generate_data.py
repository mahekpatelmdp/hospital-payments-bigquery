"""
Script to generate realistic dummy hospital payments dataset.
Run once to produce raw CSV files in the data/ directory.
"""

import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────

STATES = {
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "NY": ["New York City", "Buffalo", "Albany", "Rochester"],
    "IL": ["Chicago", "Springfield", "Peoria", "Rockford"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
    "GA": ["Atlanta", "Savannah", "Augusta", "Macon"],
    "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
    "AZ": ["Phoenix", "Tucson", "Scottsdale", "Tempe"],
}

HOSPITAL_PREFIXES = [
    "General", "Memorial", "Regional", "Community", "University",
    "St. Mary's", "St. Joseph", "Good Samaritan", "Mercy", "Sacred Heart"
]

DIAGNOSES = [
    ("Heart Attack", "I21", "Cardiovascular"),
    ("Heart Failure", "I50", "Cardiovascular"),
    ("Pneumonia", "J18", "Respiratory"),
    ("Hip/Knee Replacement", "Z96", "Orthopedic"),
    ("Stroke", "I63", "Neurological"),
    ("COPD", "J44", "Respiratory"),
    ("Sepsis", "A41", "Infectious Disease"),
    ("Kidney Failure", "N17", "Nephrology"),
    ("Diabetes Complication", "E11", "Endocrine"),
    ("Appendectomy", "K37", "General Surgery"),
]

PAYERS = ["Medicare", "Medicaid", "Private Insurance", "Self-Pay"]
PAYER_WEIGHTS = [0.45, 0.20, 0.30, 0.05]

# ── Generate Hospitals ────────────────────────────────────────────────────────

def generate_hospitals(n=200):
    rows = []
    provider_id = 100001
    for state, cities in STATES.items():
        count = n // len(STATES)
        for i in range(count):
            city = random.choice(cities)
            name = f"{random.choice(HOSPITAL_PREFIXES)} Hospital of {city}"
            rows.append({
                "provider_id": provider_id,
                "hospital_name": name,
                "address": f"{random.randint(100, 9999)} Medical Drive",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}",
                "phone": f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                "hospital_type": random.choice(["Acute Care", "Critical Access", "Specialty"]),
                "bed_count": random.randint(50, 800),
            })
            provider_id += 1
    return pd.DataFrame(rows)


# ── Generate Patients ─────────────────────────────────────────────────────────

def generate_patients(n=5000):
    rows = []
    for i in range(1, n + 1):
        age = int(np.random.normal(62, 15))
        age = max(18, min(95, age))
        rows.append({
            "patient_id": f"PAT{i:06d}",
            "age": age,
            "gender": random.choice(["M", "F"]),
            "race": random.choice(["White", "Black", "Hispanic", "Asian", "Other"]),
            "state": random.choice(list(STATES.keys())),
            "insurance_type": random.choices(PAYERS, weights=PAYER_WEIGHTS)[0],
        })
    return pd.DataFrame(rows)


# ── Generate Diagnoses Reference ─────────────────────────────────────────────

def generate_diagnoses():
    rows = []
    for name, code, category in DIAGNOSES:
        rows.append({
            "diagnosis_code": code,
            "diagnosis_name": name,
            "category": category,
            "avg_los_days": round(random.uniform(2.5, 9.5), 1),
        })
    return pd.DataFrame(rows)


# ── Generate Claims (fact table source) ──────────────────────────────────────

def generate_claims(hospitals_df, patients_df, n=20000):
    rows = []
    provider_ids = hospitals_df["provider_id"].tolist()
    patient_ids = patients_df["patient_id"].tolist()

    start_date = pd.Timestamp("2022-01-01")
    end_date = pd.Timestamp("2024-12-31")
    date_range = (end_date - start_date).days

    for i in range(1, n + 1):
        diag = random.choice(DIAGNOSES)
        base_charge = random.uniform(8000, 120000)
        payer = random.choices(PAYERS, weights=PAYER_WEIGHTS)[0]

        # Payment ratios vary by payer
        ratios = {"Medicare": 0.38, "Medicaid": 0.28, "Private Insurance": 0.52, "Self-Pay": 0.15}
        avg_payment = round(base_charge * ratios[payer] * random.uniform(0.85, 1.15), 2)
        covered_charge = round(base_charge * random.uniform(0.95, 1.05), 2)

        admit_date = start_date + pd.Timedelta(days=random.randint(0, date_range))
        los = random.randint(1, 14)
        discharge_date = admit_date + pd.Timedelta(days=los)

        national_avg = 22000
        compared_to_national = (
            "Above" if avg_payment > national_avg
            else "Below" if avg_payment < national_avg * 0.85
            else "Same"
        )

        rows.append({
            "claim_id": f"CLM{i:08d}",
            "provider_id": random.choice(provider_ids),
            "patient_id": random.choice(patient_ids),
            "diagnosis_code": diag[1],
            "admit_date": admit_date.date(),
            "discharge_date": discharge_date.date(),
            "length_of_stay": los,
            "covered_charges": covered_charge,
            "avg_payment": avg_payment,
            "payer_type": payer,
            "compared_to_national": compared_to_national,
            "readmission_flag": random.choices([0, 1], weights=[0.85, 0.15])[0],
        })

    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Generating hospitals...")
    hospitals = generate_hospitals(200)
    hospitals.to_csv("data/hospitals.csv", index=False)

    print("Generating patients...")
    patients = generate_patients(5000)
    patients.to_csv("data/patients.csv", index=False)

    print("Generating diagnoses...")
    diagnoses = generate_diagnoses()
    diagnoses.to_csv("data/diagnoses.csv", index=False)

    print("Generating claims...")
    claims = generate_claims(hospitals, patients, 20000)
    claims.to_csv("data/claims.csv", index=False)

    print("\nDone! Files written to data/:")
    for f in os.listdir("data"):
        path = f"data/{f}"
        size = os.path.getsize(path)
        print(f"  {f:30s} {size/1024:.1f} KB")
