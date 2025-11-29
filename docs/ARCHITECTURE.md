# PFMS Prototype Architecture Overview

## Overview
This prototype demonstrates an end-to-end PFMS. The major components are:

- Backend (Flask): Manages DB, auth, transactions, and ML endpoints.
- Database (SQLite): Simple feature store and model metadata storage for demos.
- ML pipeline: Two-stage categorizer (TF-IDF + GradientBoosting), IsolationForest for anomalies, and Exponential Smoothing for forecasting.
- Frontend (Flask/Jinja): Minimal dashboard allowing CSV uploads, viewing transactions, predicting categories, and seeing anomalies and forecasts.

## Scaling to Production
- Replace SQLite with a scalable DB like Postgres; add feature store (Feast) for model input features.
- Move ML training and inference to separate services (FastAPI + GPU cluster or model serving). Use a model registry (MLflow).
- Add background job processing (Celery + Redis) for retraining and heavy jobs.
- Use cloud KMS for secret management and encryption.
- For bank integration, implement Plaid/TrueLayer adapter services with OAuth and secure storage of tokens.

## Privacy & Security
- Consent ledger records user consents in the `consent` table.
- PII is encrypted with Fernet; replace with cloud KMS in production.
- JWT authentication for API access.

***
For the showcase, highlight ML architecture (two-stage categorization), privacy-first design (consent + encryption), and modularity enabling scaling to 100k MAU.
