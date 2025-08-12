from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from models import Contact, User
from sqlalchemy import or_

bp = Blueprint("contacts", __name__, url_prefix="/api/contacts")

@bp.get("")
@jwt_required()
def list_contacts():
    user_id = get_jwt_identity()
    q = (request.args.get("q") or "").strip()
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 10)), 100)

    query = db.session.query(Contact).filter(Contact.user_id == user_id)
    if q:
        pattern = f"%{q}%"
        query = query.filter(or_(Contact.name.ilike(pattern), Contact.email.ilike(pattern), Contact.phone.ilike(pattern)))

    pagination = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [c.to_dict() for c in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    })

@bp.post("")
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    contact = Contact(
        user_id=user_id,
        name=name,
        phone=(data.get("phone") or "").strip() or None,
        email=(data.get("email") or "").strip().lower() or None,
        address=(data.get("address") or "").strip() or None,
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201

@bp.get("/<int:contact_id>")
@jwt_required()
def get_contact(contact_id: int):
    user_id = get_jwt_identity()
    contact = db.session.get(Contact, contact_id)
    if not contact or contact.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    return jsonify(contact.to_dict())

@bp.put("/<int:contact_id>")
@jwt_required()
def update_contact(contact_id: int):
    user_id = get_jwt_identity()
    contact = db.session.get(Contact, contact_id)
    if not contact or contact.user_id != user_id:
        return jsonify({"error": "not found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        contact.name = name
    if "phone" in data:
        contact.phone = (data.get("phone") or "").strip() or None
    if "email" in data:
        contact.email = (data.get("email") or "").strip().lower() or None
    if "address" in data:
        contact.address = (data.get("address") or "").strip() or None

    db.session.commit()
    return jsonify(contact.to_dict())

@bp.delete("/<int:contact_id>")
@jwt_required()
def delete_contact(contact_id: int):
    user_id = get_jwt_identity()
    contact = db.session.get(Contact, contact_id)
    if not contact or contact.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "deleted"})
