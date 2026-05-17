# 🏥 Hospital Payments — Cloud Data Warehouse ETL (BigQuery)

An end-to-end ETL pipeline that loads and transforms hospital claims data into a star-schema dimensional model hosted on **Google BigQuery**.

---

## 📊 Project Overview

This project simulates a real-world data engineering workflow for a healthcare analytics team. Raw hospital claims data is generated, cleaned with Python, transformed into a dimensional model, and loaded into BigQuery for analysis.

**Stack:** Python · Pandas · Google BigQuery · SQL

---

## 🗂️ Star Schema (Dimensional Model)

```
                    ┌─────────────────┐
                    │   fact_claims   │
                    │─────────────────│
                    │ claim_key  (PK) │
                    │ hospital_key    │──► dim_hospitals
                    │ patient_key     │──► dim_patients
                    │ diagnosis_key   │──► dim_diagnoses
                    │ admit_date_key  │──► dim_date
                    │ discharge_date_key│─► dim_date
                    │ length_of_stay  │
                    │ covered_charges │
                    │ avg_payment     │
                    │ payer_type      │
                    │ compared_to_    │
                    │   national      │
                    │ readmission_flag│
                    └─────────────────┘
```

| Table | Type | Rows |
|-------|------|------|
| `fact_claims` | Fact | 20,000 |
| `dim_hospitals` | Dimension | 200 |
| `dim_patients` | Dimension | 5,000 |
| `dim_diagnoses` | Dimension | 10 |
| `dim_date` | Dimension | ~1,000 |

---

## 📁 Repository Structure

```
hospital-payments-bigquery/
├── generate_data.py          # Generates realistic dummy CSV datasets
├── 1_create_tables.py        # Creates all tables in BigQuery
├── 2_etl.py                  # Transforms and loads data into BigQuery
├── sql_queries.sql           # 10 analytical queries against the model
├── notebooks/
│   └── 3_test_queries.ipynb  # Validates schema and runs analytics
├── data/                     # Generated CSVs (git-ignored)
├── bq.cfg                    # BigQuery config (git-ignored)
├── requirements.txt
└── .gitignore
```

---

## 🚀 Setup & Usage

### 1. Prerequisites
- Python 3.9+
- A [Google Cloud](https://console.cloud.google.com/) account (free tier works)
- A GCP project with the BigQuery API enabled

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud
```bash
gcloud auth application-default login
```

### 4. Configure
Edit `bq.cfg` with your GCP project ID:
```ini
[BIGQUERY]
project_id = your-gcp-project-id
dataset    = hospital_payments
```

### 5. Generate the dataset
```bash
python generate_data.py
```

### 6. Create tables in BigQuery
```bash
python 1_create_tables.py
```

### 7. Run the ETL pipeline
```bash
python 2_etl.py
```

### 8. Validate & analyze
Open `notebooks/3_test_queries.ipynb` in Jupyter and run all cells.

---

## 🔍 Sample Business Questions Answered

- Which states have the highest average hospital payments?
- Which diagnoses have the highest readmission rates?
- How do payment amounts differ across payer types (Medicare vs. Private)?
- Which hospitals are most efficient (high volume, low avg payment)?
- How has claim volume trended month-over-month?

---

## 👤 Author

**Mahek Patel**
- GitHub: [@mahekpatelmdp](https://github.com/mahekpatelmdp)
- LinkedIn: [linkedin.com/in/yourprofile](https://www.linkedin.com/in/mahek-patel-8ba264286)

---

## 📝 License

MIT License
