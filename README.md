## OPT Project Progress Log

**Student:** Shubham Shekhar Patil  
**Email:** shubhamshekharpatil@gmail.com  
**Faculty Sponsors:** Jeffrey Saltz; Ingrid Erickson  
**Reporting Tool:** Qualtrics (OPT bi-monthly reporting)

---

## Project Overview

**Goal:** Build an end-to-end data-to-AI workflow: analyze and prepare datasets, expand the data foundation using approved public sources, and prototype an internal student-support chatbot grounded in curated content.

**Status:** **Internal demo only (not public).** Any public release will happen only after usage/compliance review.

---

## Timeline & Work Completed

## Jan 1 – Jan 15, 2026

**Focus:** Dataset understanding + readiness for modeling

**Work completed:**
- Performed exploratory data analysis (EDA): schema review, variable types, missing values, duplicates
- Generated descriptive statistics and explored distributions/relationships (correlations + categorical breakdowns)
- Identified data quality issues (outliers, inconsistent categories, skewed variables)
- Documented recommended preprocessing steps (cleaning, encoding, scaling, feature engineering)

**Outputs:**
- EDA notes and findings
- Preprocessing plan for downstream analytics/modeling

**Next steps:**
- Implement preprocessing pipeline and create a model-ready dataset

---

## Jan 16 – Jan 31, 2026

**Focus:** Next phase — data expansion + chatbot prototype (internal)

**Work completed:**
- Pivoted to incorporate content from public websites and integrated it with existing dataframes
- Built a structured ingestion workflow to collect, parse, and normalize content into a consistent dataset format
- Tracked provenance metadata (e.g., source URL and access date) and performed deduplication/quality checks
- Prototyped a student-facing chatbot concept using retrieval-based grounding (responses based on curated content)
- Tested the internal demo with sample student questions, documented failure cases, and outlined improvements
- Kept the prototype internal and non-public pending compliance/usage review

**Outputs:**
- Integrated dataset (existing DF + web-sourced DF) with documented schema/provenance fields
- Internal chatbot demo prototype + test questions + evaluation notes

**Reporting note:**
- The **Jan 16–31** option was not visible in the Qualtrics reporting period dropdown at the time of submission.  
  I shared this update by email and will enter it in Qualtrics once the period is enabled.

**Next steps:**
- Improve retrieval quality (chunking, indexing, ranking, dedup)
- Run structured evaluation with a defined set of student questions and success metrics

---

## STEM Skills Developed

- **Exploratory data analysis (EDA):** structure/pattern discovery, descriptive stats, correlations
- **Data cleaning and validation:** missing values, duplicates, outliers, inconsistencies
- **Feature engineering mindset:** encoding, scaling, transformations, derived features
- **Data engineering workflows:** ingestion, parsing, schema design, reproducibility
- **Dataset documentation & governance:** provenance tracking, versioning, clear documentation
- **Applied NLP/AI prototyping:** retrieval-grounded chatbot design, testing, error analysis, guardrails

---

## Compliance / Safety Notes (Internal Demo)

- Demo remains **private/internal** (not public-facing)
- Public content usage is treated as **subject to source constraints** (ToS/robots/access review)
- Avoid collecting/storing **personal or sensitive data**
- Prefer lightweight collection practices (rate limiting, caching) and clear provenance tracking

---

## Next Steps (Upcoming Period)

- Confirm approved sources and complete usage/compliance review
- Expand curated knowledge base and improve dataset quality
- Improve retrieval performance and answer grounding
- Prepare a short sponsor-facing summary (what works, what fails, next experiments)

---
