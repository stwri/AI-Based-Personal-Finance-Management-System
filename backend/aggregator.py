from flask import Blueprint, request, jsonify, current_app
from .db import db
from .models import AggregatorAccount, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from .encryption import encrypt, decrypt

agg_bp = Blueprint('aggregator', __name__)

PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')


@agg_bp.route('/link', methods=['GET'])
@jwt_required()
def link():
    provider = request.args.get('provider', 'mock')
    if provider == 'plaid':
        # In production, you'd call the Plaid client to generate a link token and return it
        if not PLAID_CLIENT_ID or not PLAID_SECRET:
            return jsonify({'message': 'PLAID_CLIENT_ID/PLAID_SECRET not configured. Using mock instead.'}), 200
        # Placeholder: call Plaid link/token/create here and return response
        return jsonify({'message': 'Plaid link token creation placeholder (use Plaid SDK in production)'}), 200
    else:
        # For demo, return a mock link URL and let frontend call mock exchange
        return jsonify({'link_url': '/api/aggregator/mock/link'}), 200


@agg_bp.route('/exchange', methods=['POST'])
@jwt_required()
def exchange():
    data = request.json or {}
    provider = data.get('provider', 'mock')
    token = data.get('token')
    user_id = get_jwt_identity()
    if provider == 'plaid':
        # In production, exchange public token for access token via Plaid API
        # Example (placeholder):
        return jsonify({'message': 'Plaid exchange placeholder. Provide public_token and call /item/public_token/exchange.'}), 200
    else:
        # Mock: create a linked account and return success
        acct = AggregatorAccount(user_id=user_id, provider='mock', external_id=f'mock-{token}', access_token=encrypt('mock-access-token'), item_id=f'item-{token}')
        db.session.add(acct)
        db.session.commit()
        return jsonify({'message': 'mock linked', 'account_id': acct.id}), 201


@agg_bp.route('/mock/link', methods=['GET'])
def mock_link():
    # A simple page or helper to simulate user 'link' with an aggregator
    return jsonify({'instructions': 'To simulate linking, POST to /api/aggregator/exchange with provider=mock and token=demo1'})


@agg_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync():
    # Sync transactions for all linked accounts for the user
    user_id = get_jwt_identity()
    linked = AggregatorAccount.query.filter_by(user_id=user_id).all()
    synced = 0
    for a in linked:
        if a.provider == 'plaid':
            # Placeholder: Fetch with Plaid client using decrypted access token
            # token = decrypt(a.access_token)
            # fetch and upsert transactions
            continue
        else:
            # Demo: read sample CSV and add transactions to DB for this user
            p = current_app.root_path.replace('backend', '') + 'sample_data/transactions.csv'
            try:
                df = pd.read_csv(p)
                for idx, row in df.iterrows():
                    t = Transaction(
                        account_id=f'mock_{a.id}_{row.get("account_id","default")}',
                        timestamp=pd.to_datetime(row.get('date')),
                        amount=float(row.get('amount',0)),
                        currency=row.get('currency','USD'),
                        raw_description=row.get('description',''),
                        merchant=row.get('merchant',''),
                        category=row.get('category',None)
                    )
                    db.session.add(t)
                    synced += 1
                db.session.commit()
            except Exception as e:
                current_app.logger.error('Sync failed: %s' % e)
    return jsonify({'synced': synced}), 200
