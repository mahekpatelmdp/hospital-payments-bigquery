"""
1_create_tables.py
Creates the staging dataset and all dimension/fact tables in BigQuery.
Run this before the ETL script. Safe to rerun — drops and recreates tables.
"""

from google.cloud import bigquery
import configparser

config = configparser.ConfigParser()
config.read("bq.cfg")

PROJECT_ID = config["BIGQUERY"]["project_id"]
DATASET = config["BIGQUERY"]["dataset"]

client = bigquery.Client(project=PROJECT_ID)


def run(query):
    client.query(query).result()
    print(f"  OK: {query.strip().splitlines()[0][:80]}")


def create_dataset():
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset `{DATASET}` ready.")


def drop_tables():
    tables = ["fact_claims", "dim_hospitals", "dim_patients", "dim_diagnoses", "dim_date"]
    for t in tables:
        run(f"DROP TABLE IF EXISTS `{PROJECT_ID}.{DATASET}.{t}`")


def create_dim_hospitals():
    run(f"""
    CREATE TABLE `{PROJECT_ID}.{DATASET}.dim_hospitals` (
        hospital_key      INT64     NOT NULL,
        provider_id       INT64     NOT NULL,
        hospital_name     STRING    NOT NULL,
        address           STRING,
        city              STRING    NOT NULL,
        state             STRING    NOT NULL,
        zip_code          STRING,
        phone             STRING,
        hospital_type     STRING,
        bed_count         INT64
    )
    """)


def create_dim_patients():
    run(f"""
    CREATE TABLE `{PROJECT_ID}.{DATASET}.dim_patients` (
        patient_key       INT64     NOT NULL,
        patient_id        STRING    NOT NULL,
        age               INT64,
        age_group         STRING,
        gender            STRING,
        race              STRING,
        state             STRING,
        insurance_type    STRING
    )
    """)


def create_dim_diagnoses():
    run(f"""
    CREATE TABLE `{PROJECT_ID}.{DATASET}.dim_diagnoses` (
        diagnosis_key     INT64     NOT NULL,
        diagnosis_code    STRING    NOT NULL,
        diagnosis_name    STRING    NOT NULL,
        category          STRING    NOT NULL,
        avg_los_days      FLOAT64
    )
    """)


def create_dim_date():
    run(f"""
    CREATE TABLE `{PROJECT_ID}.{DATASET}.dim_date` (
        date_key          INT64     NOT NULL,
        full_date         DATE      NOT NULL,
        year              INT64     NOT NULL,
        quarter           INT64     NOT NULL,
        month             INT64     NOT NULL,
        month_name        STRING    NOT NULL,
        week              INT64     NOT NULL,
        day_of_week       INT64     NOT NULL,
        day_name          STRING    NOT NULL,
        is_weekend        BOOL      NOT NULL
    )
    """)


def create_fact_claims():
    run(f"""
    CREATE TABLE `{PROJECT_ID}.{DATASET}.fact_claims` (
        claim_key               INT64     NOT NULL,
        claim_id                STRING    NOT NULL,
        hospital_key            INT64     NOT NULL,
        patient_key             INT64     NOT NULL,
        diagnosis_key           INT64     NOT NULL,
        admit_date_key          INT64     NOT NULL,
        discharge_date_key      INT64     NOT NULL,
        length_of_stay          INT64,
        covered_charges         FLOAT64,
        avg_payment             FLOAT64,
        payer_type              STRING,
        compared_to_national    STRING,
        readmission_flag        INT64
    )
    """)


if __name__ == "__main__":
    print("Creating dataset...")
    create_dataset()

    print("\nDropping existing tables...")
    drop_tables()

    print("\nCreating dimension tables...")
    create_dim_hospitals()
    create_dim_patients()
    create_dim_diagnoses()
    create_dim_date()

    print("\nCreating fact table...")
    create_fact_claims()

    print("\nAll tables created successfully.")
