from flask import Blueprint, request, jsonify
from .db import db
from .models import Consent
from flask_jwt_extended import jwt_required, get_jwt_identity

consent_bp = Blueprint('consent', __name__)


@consent_bp.route('/consent', methods=['POST'])
@jwt_required()
def give_consent():
    data = request.json or {}
    scope = data.get('scope', 'transactions')
    user = get_jwt_identity()
    c = Consent(user_id=user, scope=scope)
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'consented'})


@consent_bp.route('/consent/<int:id>', methods=['DELETE'])
@jwt_required()
def revoke_consent(id):
    c = Consent.query.get(id)
    if not c:
        return jsonify({'message': 'not found'}), 404
    c.revoked = True
    db.session.commit()
    return jsonify({'message': 'revoked'})
