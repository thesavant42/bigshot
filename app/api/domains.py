"""
Domain API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import Domain
from app.utils.responses import success_response, error_response, paginated_response
from app.services.enumeration import EnumerationService
from sqlalchemy import or_

domains_bp = Blueprint("domains", __name__)


@domains_bp.route("/domains", methods=["GET"])
@jwt_required()
def get_domains():
    """Get all domains with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        root_domain = request.args.get("root_domain")
        source = request.args.get("source")
        search = request.args.get("search")

        # Build query
        query = Domain.query

        if root_domain:
            query = query.filter(Domain.root_domain == root_domain)

        if source:
            query = query.filter(Domain.source == source)

        if search:
            query = query.filter(
                or_(
                    Domain.subdomain.contains(search),
                    Domain.root_domain.contains(search),
                    Domain.tags.contains(search),
                )
            )

        # Order by subdomain
        query = query.order_by(Domain.subdomain)

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        domains = [domain.to_dict() for domain in pagination.items]

        return paginated_response(
            data=domains,
            total=pagination.total,
            page=page,
            per_page=per_page,
            pages=pagination.pages,
        )

    except Exception as e:
        return error_response(f"Failed to fetch domains: {str(e)}", 500)


@domains_bp.route("/domains/<int:domain_id>", methods=["GET"])
@jwt_required()
def get_domain(domain_id):
    """Get a specific domain"""
    try:
        domain = db.session.get(Domain, domain_id)
        if not domain:
            return error_response("Domain not found", 404)
        return success_response(domain.to_dict())
    except Exception as e:
        return error_response(f"Failed to fetch domain: {str(e)}", 500)


@domains_bp.route("/domains", methods=["POST"])
@jwt_required()
def create_domain():
    """Create a new domain"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["root_domain", "subdomain", "source"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        # Check for duplicate
        existing = Domain.query.filter_by(
            subdomain=data["subdomain"], source=data["source"]
        ).first()

        if existing:
            return error_response("Domain already exists for this source", 409)

        # Create domain
        domain = Domain(
            root_domain=data["root_domain"],
            subdomain=data["subdomain"],
            source=data["source"],
            tags=",".join(data.get("tags", [])),
            cdx_indexed=data.get("cdx_indexed", False),
        )

        db.session.add(domain)
        db.session.commit()

        return success_response(domain.to_dict(), 201)

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create domain: {str(e)}", 500)


@domains_bp.route("/domains/<int:domain_id>", methods=["PUT"])
@jwt_required()
def update_domain(domain_id):
    """Update a domain"""
    try:
        domain = db.session.get(Domain, domain_id)
        if not domain:
            return error_response("Domain not found", 404)

        data = request.get_json()

        # Update fields
        if "tags" in data:
            domain.tags = ",".join(data["tags"])
        if "cdx_indexed" in data:
            domain.cdx_indexed = data["cdx_indexed"]

        db.session.commit()
        return success_response(domain.to_dict())

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update domain: {str(e)}", 500)


@domains_bp.route("/domains/<int:domain_id>", methods=["DELETE"])
@jwt_required()
def delete_domain(domain_id):
    """Delete a domain"""
    try:
        domain = db.session.get(Domain, domain_id)
        if not domain:
            return error_response("Domain not found", 404)

        db.session.delete(domain)
        db.session.commit()

        return success_response({"message": "Domain deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete domain: {str(e)}", 500)


@domains_bp.route("/domains/bulk", methods=["POST"])
@jwt_required()
def bulk_domain_operation():
    """Perform bulk operations on domains"""
    try:
        data = request.get_json()
        operation = data.get("operation")
        domain_ids = data.get("domain_ids", [])

        if not operation or not domain_ids:
            return error_response("Missing operation or domain_ids", 400)

        domains = Domain.query.filter(Domain.id.in_(domain_ids)).all()

        if operation == "delete":
            for domain in domains:
                db.session.delete(domain)
        elif operation == "update_tags":
            new_tags = ",".join(data.get("tags", []))
            for domain in domains:
                domain.tags = new_tags
        else:
            return error_response(f"Unknown operation: {operation}", 400)

        db.session.commit()
        return success_response({"message": f"Bulk {operation} completed successfully"})

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to perform bulk operation: {str(e)}", 500)


@domains_bp.route("/domains/enumerate", methods=["POST"])
@jwt_required()
def enumerate_domains():
    """Start domain enumeration job"""
    try:
        data = request.get_json()

        # Validate required fields
        if "domains" not in data:
            return error_response("Missing required field: domains", 400)

        domains = data["domains"]
        sources = data.get("sources", ["crt.sh"])
        options = data.get("options", {})

        # Start enumeration job
        enumeration_service = EnumerationService()
        job = enumeration_service.start_enumeration(
            domains=domains, sources=sources, options=options
        )

        return success_response(job.to_dict(), 202)

    except Exception as e:
        return error_response(f"Failed to start enumeration: {str(e)}", 500)


@domains_bp.route("/domains/hierarchy/<root_domain>", methods=["GET"])
@jwt_required()
def get_domain_hierarchy(root_domain):
    """Get hierarchical domain structure"""
    try:
        domains = (
            Domain.query.filter_by(root_domain=root_domain)
            .order_by(Domain.subdomain)
            .all()
        )

        # Build hierarchy
        hierarchy = {}
        for domain in domains:
            subdomain = domain.subdomain
            parts = subdomain.split(".")

            # Build nested structure
            current = hierarchy
            for part in reversed(parts):
                if part not in current:
                    current[part] = {"domains": [], "children": {}}
                current = current[part]["children"]

            # Add domain info
            leaf_part = parts[-1]
            if leaf_part in hierarchy:
                hierarchy[leaf_part]["domains"].append(domain.to_dict())

        return success_response(hierarchy)

    except Exception as e:
        return error_response(f"Failed to build hierarchy: {str(e)}", 500)
