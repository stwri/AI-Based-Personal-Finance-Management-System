# PFMS Backend

This is a demo backend for the PFMS prototype. It exposes a few endpoints:

- POST /api/auth/register - register user with JSON {username, password}
- POST /api/auth/login - login returns JWT
- POST /api/transactions/upload - upload CSV files (auth required)
- GET /api/transactions - list recent transactions
- POST /api/transactions/<id>/categorize - update a category and trigger retraining (auth required)
- POST /api/models/retrain - force retrain of the categorizer
- POST /api/models/predict - predict category for a description
- GET /api/models/anomalies - list anomalies
- GET /api/models/forecast - forecast amounts (periods param)

Run locally:

```
python -m venv .venv; .\.venv\Scripts\Activate; python -m pip install -r requirements.txt
python run.py

Run tests:

```
pytest -q

Plaid/TrueLayer integration (demo & sandbox)
-------------------------------------------
This project includes a demo aggregator adapter and a `mock` provider that allows you to simulate linking a bank account and syncing transactions.

To use a real aggregator (Plaid sandbox):
1. Sign up for a Plaid sandbox account and get a `PLAID_CLIENT_ID` and `PLAID_SECRET`.
2. Add them to your `.env` or `.env.example` and restart the app:

```
setx PLAID_CLIENT_ID <your-client-id>
setx PLAID_SECRET <your-secret>
setx PLAID_ENV sandbox
```
3. Implement link token creation and exchange in `backend/aggregator.py` using the Plaid Python SDK (code paths are marked as placeholders).

For demo / lightweight testing without integration credentials, use the mock flow:
1. Link mock bank from the dashboard by clicking "Link Mock Bank".
2. Press "Sync Linked Accounts" to import transactions from `sample_data/transactions.csv` into the app.

```
```

The prototype uses simple file-backed models for demonstration. In production, use a real feature store and KMS for key management.
