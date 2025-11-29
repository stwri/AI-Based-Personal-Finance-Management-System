import os
from pathlib import Path
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd
from datetime import datetime
from .db import db
from .models import Transaction, ModelMetadata
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import joblib

MODELS_DIR = Path(__file__).resolve().parent / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class ModelManager:
    def __init__(self):
        self.model_path = MODELS_DIR / 'cat_model.joblib'
        self.vec_path = MODELS_DIR / 'vectorizer.joblib'
        self.if_path = MODELS_DIR / 'anomaly.joblib'

    def ensure_trained(self):
        if not self.model_path.exists() or not self.vec_path.exists():
            self.train_initial()

    def train_initial(self):
        # Load data from transactions with category
        df = self._get_labeled_data()
        if df.empty:
            # seed with some fabricated rows
            df = pd.DataFrame([
                {'description': 'Starbucks coffee', 'category': 'Food & Drink'},
                {'description': 'Shell gas station', 'category': 'Transport'},
                {'description': 'Spotify subscription', 'category': 'Subscriptions'},
                {'description': 'Salary Nov', 'category': 'Income'},
            ])
        X = df['description'].astype(str).tolist()
        y = df['category'].astype(str).tolist()
        vec = TfidfVectorizer(ngram_range=(1,2), max_features=2048)
        Xv = vec.fit_transform(X)
        clf = GradientBoostingClassifier(n_estimators=50)
        clf.fit(Xv, y)
        dump(vec, self.vec_path)
        dump(clf, self.model_path)

        # anomaly model on amounts
        amounts = self._get_amounts()
        if not amounts.empty:
            iso = IsolationForest(contamination=0.02, random_state=42)
            iso.fit(amounts.values.reshape(-1,1))
            dump(iso, self.if_path)

        self._save_metadata('categorizer', 'v1')

    def _get_labeled_data(self):
        rows = Transaction.query.filter(Transaction.category != None).all()
        data = [{'description': r.raw_description or '', 'category': r.category} for r in rows]
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)

    def _get_amounts(self):
        rows = Transaction.query.all()
        arr = [r.amount for r in rows if r.amount is not None]
        return pd.Series(arr)

    def predict_category(self, description):
        self.ensure_trained()
        vec = load(self.vec_path)
        clf = load(self.model_path)
        Xv = vec.transform([description])
        return clf.predict(Xv)[0]

    def detect_anomalies(self):
        self.ensure_trained()
        if not self.if_path.exists():
            return []
        iso = load(self.if_path)
        rows = Transaction.query.all()
        amounts = np.array([r.amount for r in rows]).reshape(-1,1)
        preds = iso.predict(amounts)
        anomalies = [rows[i] for i,p in enumerate(preds) if p==-1]
        return anomalies

    def incremental_train(self):
        # Simple retrain on all labeled data
        df = self._get_labeled_data()
        if df.empty:
            return
        vec = TfidfVectorizer(ngram_range=(1,2), max_features=2048)
        Xv = vec.fit_transform(df['description'].astype(str))
        clf = GradientBoostingClassifier(n_estimators=50)
        clf.fit(Xv, df['category'])
        dump(vec, self.vec_path)
        dump(clf, self.model_path)
        # update anomaly model
        amounts = self._get_amounts()
        if not amounts.empty:
            iso = IsolationForest(contamination=0.02, random_state=42)
            iso.fit(amounts.values.reshape(-1,1))
            dump(iso, self.if_path)
        self._save_metadata('categorizer', 'v1')

    def forecast(self, account_id=None, periods=7):
        # Simple daily aggregated forecast for amount sums
        rows = Transaction.query.order_by(Transaction.timestamp.asc()).all()
        df = pd.DataFrame([{'timestamp': r.timestamp, 'amount': r.amount} for r in rows if r.timestamp and r.amount is not None])
        if df.empty:
            return []
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily = df.groupby('date').sum()['amount']
        daily.index = pd.to_datetime(daily.index)
        model = ExponentialSmoothing(daily, trend='add', seasonal=None)
        hw = model.fit()
        future = hw.forecast(periods)
        return [{'date': d.strftime('%Y-%m-%d'), 'forecast': float(v)} for d, v in future.items()]

    def _save_metadata(self, name, version):
        mm = ModelMetadata.query.filter_by(name=name).first() or ModelMetadata(name=name)
        mm.version = version
        mm.last_trained_at = datetime.utcnow()
        db.session.add(mm)
        db.session.commit()
