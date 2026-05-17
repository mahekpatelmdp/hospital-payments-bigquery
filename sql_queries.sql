-- sql_queries.py
-- Analytical queries to validate the dimensional model and answer business questions.
-- Replace {PROJECT}.{DATASET} with your actual project and dataset IDs.

-- ── 1. Row counts per table ───────────────────────────────────────────────────

SELECT 'fact_claims'    AS tbl, COUNT(*) AS rows FROM `{PROJECT}.{DATASET}.fact_claims`
UNION ALL
SELECT 'dim_hospitals',          COUNT(*) FROM `{PROJECT}.{DATASET}.dim_hospitals`
UNION ALL
SELECT 'dim_patients',           COUNT(*) FROM `{PROJECT}.{DATASET}.dim_patients`
UNION ALL
SELECT 'dim_diagnoses',          COUNT(*) FROM `{PROJECT}.{DATASET}.dim_diagnoses`
UNION ALL
SELECT 'dim_date',               COUNT(*) FROM `{PROJECT}.{DATASET}.dim_date`;


-- ── 2. Total claims and avg payment by state ──────────────────────────────────

SELECT
    h.state,
    COUNT(f.claim_key)          AS total_claims,
    ROUND(AVG(f.avg_payment), 2) AS avg_payment,
    ROUND(SUM(f.avg_payment), 2) AS total_payments
FROM `{PROJECT}.{DATASET}.fact_claims`     f
JOIN `{PROJECT}.{DATASET}.dim_hospitals`   h ON f.hospital_key = h.hospital_key
GROUP BY h.state
ORDER BY total_payments DESC;


-- ── 3. Top 10 hospitals by total payments ────────────────────────────────────

SELECT
    h.hospital_name,
    h.city,
    h.state,
    COUNT(f.claim_key)           AS total_claims,
    ROUND(SUM(f.avg_payment), 2) AS total_payments
FROM `{PROJECT}.{DATASET}.fact_claims`   f
JOIN `{PROJECT}.{DATASET}.dim_hospitals` h ON f.hospital_key = h.hospital_key
GROUP BY h.hospital_name, h.city, h.state
ORDER BY total_payments DESC
LIMIT 10;


-- ── 4. Payment by diagnosis category ─────────────────────────────────────────

SELECT
    d.category,
    d.diagnosis_name,
    COUNT(f.claim_key)            AS total_claims,
    ROUND(AVG(f.avg_payment), 2)  AS avg_payment,
    ROUND(AVG(f.length_of_stay), 1) AS avg_los
FROM `{PROJECT}.{DATASET}.fact_claims`    f
JOIN `{PROJECT}.{DATASET}.dim_diagnoses`  d ON f.diagnosis_key = d.diagnosis_key
GROUP BY d.category, d.diagnosis_name
ORDER BY avg_payment DESC;


-- ── 5. Payer mix and average payment by payer type ───────────────────────────

SELECT
    payer_type,
    COUNT(*)                      AS total_claims,
    ROUND(AVG(avg_payment), 2)    AS avg_payment,
    ROUND(AVG(covered_charges), 2) AS avg_covered_charge,
    ROUND(AVG(avg_payment / NULLIF(covered_charges, 0)) * 100, 1) AS payment_ratio_pct
FROM `{PROJECT}.{DATASET}.fact_claims`
GROUP BY payer_type
ORDER BY avg_payment DESC;


-- ── 6. Monthly claim volume and payments (trend) ─────────────────────────────

SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(f.claim_key)            AS total_claims,
    ROUND(AVG(f.avg_payment), 2)  AS avg_payment
FROM `{PROJECT}.{DATASET}.fact_claims` f
JOIN `{PROJECT}.{DATASET}.dim_date`    dd ON f.admit_date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- ── 7. Readmission rate by diagnosis ─────────────────────────────────────────

SELECT
    d.diagnosis_name,
    COUNT(*)                                          AS total_claims,
    SUM(f.readmission_flag)                           AS readmissions,
    ROUND(AVG(f.readmission_flag) * 100, 1)           AS readmission_rate_pct
FROM `{PROJECT}.{DATASET}.fact_claims`   f
JOIN `{PROJECT}.{DATASET}.dim_diagnoses` d ON f.diagnosis_key = d.diagnosis_key
GROUP BY d.diagnosis_name
ORDER BY readmission_rate_pct DESC;


-- ── 8. Payments vs national average by state ─────────────────────────────────

SELECT
    h.state,
    f.compared_to_national,
    COUNT(*) AS claim_count
FROM `{PROJECT}.{DATASET}.fact_claims`   f
JOIN `{PROJECT}.{DATASET}.dim_hospitals` h ON f.hospital_key = h.hospital_key
GROUP BY h.state, f.compared_to_national
ORDER BY h.state, f.compared_to_national;


-- ── 9. Age group analysis ─────────────────────────────────────────────────────

SELECT
    p.age_group,
    p.insurance_type,
    COUNT(f.claim_key)            AS total_claims,
    ROUND(AVG(f.avg_payment), 2)  AS avg_payment,
    ROUND(AVG(f.length_of_stay), 1) AS avg_los
FROM `{PROJECT}.{DATASET}.fact_claims`  f
JOIN `{PROJECT}.{DATASET}.dim_patients` p ON f.patient_key = p.patient_key
GROUP BY p.age_group, p.insurance_type
ORDER BY p.age_group, p.insurance_type;


-- ── 10. Hospital efficiency: high volume, low avg payment ────────────────────

SELECT
    h.hospital_name,
    h.state,
    h.bed_count,
    COUNT(f.claim_key)            AS total_claims,
    ROUND(AVG(f.avg_payment), 2)  AS avg_payment,
    ROUND(AVG(f.length_of_stay), 1) AS avg_los
FROM `{PROJECT}.{DATASET}.fact_claims`   f
JOIN `{PROJECT}.{DATASET}.dim_hospitals` h ON f.hospital_key = h.hospital_key
GROUP BY h.hospital_name, h.state, h.bed_count
HAVING total_claims > 100
ORDER BY avg_payment ASC
LIMIT 15;
