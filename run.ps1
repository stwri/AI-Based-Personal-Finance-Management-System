# PowerShell script to run the prototype
python -m venv .venv; .\.venv\Scripts\Activate; python -m pip install -r backend/requirements.txt; cd backend; python seed.py; python run.py
