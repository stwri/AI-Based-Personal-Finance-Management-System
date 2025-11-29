from .db import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    email = Column(String(256), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    account_id = Column(String(256))
    timestamp = Column(DateTime)
    amount = Column(Float)
    currency = Column(String(8), default='USD')
    raw_description = Column(Text)
    merchant = Column(String(256))
    category = Column(String(256))
    user_note = Column(Text)
    # encrypted fields may be stored as blob in production


class Consent(db.Model):
    __tablename__ = 'consent'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    scope = Column(String(256))
    consented_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class ModelMetadata(db.Model):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    version = Column(String(128))
    last_trained_at = Column(DateTime)
    metrics = Column(Text)


class AggregatorAccount(db.Model):
    __tablename__ = 'aggregator_accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    provider = Column(String(64))
    external_id = Column(String(256))
    access_token = Column(String(512))
    item_id = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)

