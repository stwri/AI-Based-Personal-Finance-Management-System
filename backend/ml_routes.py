from flask import Blueprint, request, jsonify
from .ml_pipeline import ModelManager
from flask_jwt_extended import jwt_required

model_bp = Blueprint('models', __name__)
mm = ModelManager()


@model_bp.route('/predict', methods=['POST'])
@jwt_required(optional=True)
def predict():
    desc = (request.json or {}).get('description', '')
    if not desc:
        return jsonify({'message': 'description required'}), 400
    category = mm.predict_category(desc)
    return jsonify({'category': category})


@model_bp.route('/retrain', methods=['POST'])
@jwt_required()
def retrain():
    mm.incremental_train()
    return jsonify({'message': 'retrained'}), 200


@model_bp.route('/anomalies', methods=['GET'])
@jwt_required()
def anomalies():
    anomalies = mm.detect_anomalies()
    return jsonify([{'id': a.id, 'amount': a.amount, 'description': a.raw_description} for a in anomalies])


@model_bp.route('/forecast', methods=['GET'])
@jwt_required(optional=True)
def forecast():
    periods = int(request.args.get('periods', 7))
    fc = mm.forecast(periods=periods)
    return jsonify(fc)
