# PFMS - AI-Based Personal Finance Management System (Prototype)

This prototype demonstrates a privacy-first PFMS with the following features:
- Transaction ingestion via CSV uploads
- Two-stage ML categorization (text vector embeddings + GradientBoostingClassifier)
- Anomaly detection (Isolation Forest)
- Short-term forecasting (simple ExponentialSmoothing)
- Consent ledger and PII field encryption (Fernet; swapable to cloud KMS)
- Small Flask API and minimal dashboard

This is a demo scaffold for a final-year project; it's intentionally lightweight and contains stubs where production-ready code should be used.

## Highlights (presentations talking points)
- Two-stage ML categorization: text vectorization (TF-IDF) + GradientBoostingClassifier.
- Feature-store demo: SQLite used as a simple store; Model metadata table included for tracking.
- Incremental retraining: user corrections call a retrain method.
- Privacy-first ledger: Consent records and symmetric encryption for PII.
- Modular architecture: Flask blueprints, ML pipeline separated, easy to scale into microservices.

## Production notes (if you expand this for a deployment)
- Use full embeddings from sentence-transformers or a cloud embedding service for staging vs production trade-offs.
- Use a managed DB (Postgres) and a stream for ingestion (Kafka / PubSub); use Celery or RQ for background retraining.
- Use cloud KMS (GCP KMS / AWS KMS / Azure Key Vault) to manage encryption keys and rotate them.
- Replace simple anomaly detection with streaming IsolationForest or online models and alerts via webhooks.
- Implement bank aggregator integration (Plaid, TrueLayer) using OAuth2 and tokenized account links.


## Structure
- `backend/` - Flask API, ML models, database models (SQLite), and CLI
- `frontend/` - Minimal dashboard templates (Flask/Jinja based) and static files
- `sample_data/` - Example CSV and seeded transactions

## Quickstart (Windows PowerShell)

Install python dependencies:

```
python -m venv .venv; .\.venv\Scripts\Activate; python -m pip install -r backend/requirements.txt
```

Run the backend server:

```
cd backend; .\.venv\Scripts\Activate; python run.py
```

Open the dashboard: http://127.0.0.1:5000

## Notes
- This implementation uses SQLite and local file persistence for simplicity. Swap to a managed DB and proper KMS for production.
- ML models are trained on sample data and updated incrementally as corrections arrive.
- For large-scale usage, you'd add background workers, message queues, and proper retraining pipelines.

---

If you'd like, I can add OAuth / bank aggregator integration, more advanced forecasting, or a React-based frontend next.