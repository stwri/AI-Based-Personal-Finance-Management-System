from flask import Blueprint, request, jsonify, current_app
from .db import db
from .models import Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
from datetime import datetime
from io import StringIO
import os

tx_bp = Blueprint('transactions', __name__)


@tx_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_transactions():
    # expects 'file' multipart form
    if 'file' not in request.files:
        return jsonify({'message': 'file missing'}), 400
    csv_file = request.files['file']
    content = csv_file.read().decode('utf-8')
    df = pd.read_csv(StringIO(content))
    added = 0
    for idx, row in df.iterrows():
        timestamp = None
        try:
            timestamp = pd.to_datetime(row.get('timestamp') or row.get('date'))
        except Exception:
            timestamp = datetime.utcnow()
        t = Transaction(
            account_id=str(row.get('account_id', 'default')),
            timestamp=timestamp,
            amount=float(row.get('amount', 0.0)),
            currency=row.get('currency', 'USD'),
            raw_description=row.get('description', row.get('raw_description', '')), 
            merchant=row.get('merchant', ''),
            category=row.get('category', None),
        )
        db.session.add(t)
        added += 1
    db.session.commit()
    return jsonify({'message': f'added {added} transactions'}), 201


@tx_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def list_transactions():
    args = request.args
    # Simple listing, limit 100
    txs = Transaction.query.order_by(Transaction.timestamp.desc()).limit(200).all()
    result = []
    for t in txs:
        result.append({
            'id': t.id,
            'timestamp': t.timestamp.isoformat() if t.timestamp else None,
            'amount': t.amount,
            'currency': t.currency,
            'description': t.raw_description,
            'merchant': t.merchant,
            'category': t.category,
        })
    return jsonify(result)


@tx_bp.route('/<int:tx_id>/categorize', methods=['POST'])
@jwt_required()
def categorize_tx(tx_id):
    # user provides category correction; we store and trigger incremental retrain
    data = request.json or {}
    new_cat = data.get('category')
    if not new_cat:
        return jsonify({'message': 'category required'}), 400
    t = Transaction.query.get(tx_id)
    if not t:
        return jsonify({'message': 'not found'}), 404
    t.category = new_cat
    db.session.commit()

    # TODO: queue or trigger retraining; for prototype, just call retrain endpoint synchronously
    from .ml_pipeline import ModelManager
    mm = ModelManager()
    mm.incremental_train()

    return jsonify({'message': 'updated'}), 200
