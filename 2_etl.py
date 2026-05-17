"""
2_etl.py
Reads raw CSVs, transforms them into dimensional model, and loads into BigQuery.
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
import configparser

config = configparser.ConfigParser()
config.read("bq.cfg")

PROJECT_ID = config["BIGQUERY"]["project_id"]
DATASET = config["BIGQUERY"]["dataset"]

client = bigquery.Client(project=PROJECT_ID)


def load_table(df, table_name):
    table_ref = f"{PROJECT_ID}.{DATASET}.{table_name}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"  Loaded {len(df):,} rows → {table_name}")


# ── Dimension Transforms ──────────────────────────────────────────────────────

def transform_dim_hospitals(df):
    df = df.copy()
    df.insert(0, "hospital_key", range(1, len(df) + 1))
    return df


def transform_dim_patients(df):
    df = df.copy()

    def age_group(age):
        if age < 30:   return "18-29"
        if age < 45:   return "30-44"
        if age < 60:   return "45-59"
        if age < 75:   return "60-74"
        return "75+"

    df["age_group"] = df["age"].apply(age_group)
    df.insert(0, "patient_key", range(1, len(df) + 1))
    return df


def transform_dim_diagnoses(df):
    df = df.copy()
    df.insert(0, "diagnosis_key", range(1, len(df) + 1))
    return df


def transform_dim_date(claims_df):
    admit_dates = pd.to_datetime(claims_df["admit_date"])
    discharge_dates = pd.to_datetime(claims_df["discharge_date"])
    all_dates = pd.Series(pd.concat([admit_dates, discharge_dates]).unique()).sort_values()
    all_dates = pd.to_datetime(all_dates)

    df = pd.DataFrame({"full_date": all_dates})
    df["date_key"] = df["full_date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["full_date"].dt.year
    df["quarter"] = df["full_date"].dt.quarter
    df["month"] = df["full_date"].dt.month
    df["month_name"] = df["full_date"].dt.strftime("%B")
    df["week"] = df["full_date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["full_date"].dt.dayofweek
    df["day_name"] = df["full_date"].dt.strftime("%A")
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    df["full_date"] = df["full_date"].dt.date
    return df.drop_duplicates(subset="date_key").reset_index(drop=True)


def transform_fact_claims(claims_df, hospitals_dim, patients_dim, diagnoses_dim, date_dim):
    df = claims_df.copy()

    # Build lookup maps
    hosp_map = dict(zip(hospitals_dim["provider_id"], hospitals_dim["hospital_key"]))
    pat_map = dict(zip(patients_dim["patient_id"], patients_dim["patient_key"]))
    diag_map = dict(zip(diagnoses_dim["diagnosis_code"], diagnoses_dim["diagnosis_key"]))
    date_map = dict(zip(date_dim["date_key"], date_dim["date_key"]))  # key = YYYYMMDD int

    def to_date_key(d):
        return int(pd.Timestamp(d).strftime("%Y%m%d"))

    df["hospital_key"] = df["provider_id"].map(hosp_map)
    df["patient_key"] = df["patient_id"].map(pat_map)
    df["diagnosis_key"] = df["diagnosis_code"].map(diag_map)
    df["admit_date_key"] = df["admit_date"].apply(to_date_key)
    df["discharge_date_key"] = df["discharge_date"].apply(to_date_key)
    df.insert(0, "claim_key", range(1, len(df) + 1))

    fact_cols = [
        "claim_key", "claim_id", "hospital_key", "patient_key", "diagnosis_key",
        "admit_date_key", "discharge_date_key", "length_of_stay",
        "covered_charges", "avg_payment", "payer_type",
        "compared_to_national", "readmission_flag"
    ]
    return df[fact_cols]


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Reading source CSVs...")
    hospitals_raw = pd.read_csv("data/hospitals.csv")
    patients_raw = pd.read_csv("data/patients.csv")
    diagnoses_raw = pd.read_csv("data/diagnoses.csv")
    claims_raw = pd.read_csv("data/claims.csv")
    print(f"  claims: {len(claims_raw):,} rows")

    print("\nTransforming dimensions...")
    dim_hospitals = transform_dim_hospitals(hospitals_raw)
    dim_patients = transform_dim_patients(patients_raw)
    dim_diagnoses = transform_dim_diagnoses(diagnoses_raw)
    dim_date = transform_dim_date(claims_raw)

    print("\nTransforming fact table...")
    fact_claims = transform_fact_claims(
        claims_raw, dim_hospitals, dim_patients, dim_diagnoses, dim_date
    )

    print("\nLoading into BigQuery...")
    load_table(dim_hospitals, "dim_hospitals")
    load_table(dim_patients, "dim_patients")
    load_table(dim_diagnoses, "dim_diagnoses")
    load_table(dim_date, "dim_date")
    load_table(fact_claims, "fact_claims")

    print("\nETL complete.")
