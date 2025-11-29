from .db import db
from .models import Transaction
import pandas as pd
from datetime import datetime
from pathlib import Path

def seed_db(app):
    with app.app_context():
        p = Path(__file__).resolve().parents[1] / 'sample_data' / 'transactions.csv'
        df = pd.read_csv(p)
        for idx, row in df.iterrows():
            tx = Transaction(
                account_id=row.get('account_id', 'default'),
                timestamp=pd.to_datetime(row.get('date')),
                amount=float(row.get('amount', 0.0)),
                currency=row.get('currency', 'USD'),
                raw_description=row.get('description', ''),
                merchant=row.get('merchant', ''),
                category=row.get('category', None),
            )
            db.session.add(tx)
        db.session.commit()
        print('seeded database')

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_db(app)
