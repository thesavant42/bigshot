"""
Data processing tasks for normalization and deduplication
"""

import json
from datetime import datetime
from celery import current_task
from celery_app import celery_app
from app import db
from app.models.models import Domain, Job
from sqlalchemy import func


@celery_app.task(bind=True, name="normalize_domains")
def normalize_domains_task(self, job_id=None):
    """
    Background task for normalizing domain data

    Args:
        job_id: Optional job ID to track progress
    """

    try:
        # Get or create job record
        if job_id:
            job = Job.query.get(job_id)
            if not job:
                job = Job(type="data_normalization", status="running", progress=0)
                db.session.add(job)
                db.session.commit()
        else:
            job = Job(type="data_normalization", status="running", progress=0)
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        # Get all domains that need normalization
        domains = Domain.query.all()
        total_domains = len(domains)
        processed_domains = 0
        normalized_count = 0

        for domain in domains:
            try:
                # Normalize subdomain
                original_subdomain = domain.subdomain
                normalized_subdomain = _normalize_domain(original_subdomain)

                # Check if normalization changed the domain
                if normalized_subdomain != original_subdomain:
                    # Check if normalized domain already exists
                    existing = Domain.query.filter_by(
                        subdomain=normalized_subdomain, source=domain.source
                    ).first()

                    if existing:
                        # Merge tags and delete duplicate
                        existing_tags = set(
                            existing.tags.split(",") if existing.tags else []
                        )
                        new_tags = set(domain.tags.split(",") if domain.tags else [])
                        merged_tags = existing_tags.union(new_tags)
                        existing.tags = ",".join(filter(None, merged_tags))
                        existing.updated_at = datetime.utcnow()
                        db.session.delete(domain)
                        normalized_count += 1
                    else:
                        # Update with normalized subdomain
                        domain.subdomain = normalized_subdomain
                        domain.updated_at = datetime.utcnow()
                        normalized_count += 1

                processed_domains += 1

                # Update progress
                progress = int((processed_domains / total_domains) * 100)
                job.progress = progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": processed_domains,
                        "total": total_domains,
                        "normalized": normalized_count,
                        "progress": progress,
                    },
                )

                # Commit periodically
                if processed_domains % 100 == 0:
                    db.session.commit()

            except Exception as e:
                print(f"Error normalizing domain {domain.subdomain}: {e}")
                processed_domains += 1

        # Final commit
        db.session.commit()

        # Update job with final results
        job.status = "completed"
        job.progress = 100
        job.result = json.dumps(
            {
                "total_processed": processed_domains,
                "normalized_count": normalized_count,
                "completion_time": datetime.utcnow().isoformat(),
            }
        )
        db.session.commit()

        return {
            "status": "completed",
            "total_processed": processed_domains,
            "normalized_count": normalized_count,
        }

    except Exception as e:
        # Update job with error
        if job_id:
            job = Job.query.get(job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.session.commit()
        raise


@celery_app.task(bind=True, name="deduplicate_domains")
def deduplicate_domains_task(self, job_id=None):
    """
    Background task for deduplicating domain data

    Args:
        job_id: Optional job ID to track progress
    """

    try:
        # Get or create job record
        if job_id:
            job = Job.query.get(job_id)
            if not job:
                job = Job(type="data_deduplication", status="running", progress=0)
                db.session.add(job)
                db.session.commit()
        else:
            job = Job(type="data_deduplication", status="running", progress=0)
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        # Find duplicate domains (same subdomain, different sources)
        duplicate_query = (
            db.session.query(Domain.subdomain, func.count(Domain.id).label("count"))
            .group_by(Domain.subdomain)
            .having(func.count(Domain.id) > 1)
        )

        duplicates = duplicate_query.all()
        total_duplicates = len(duplicates)
        processed_duplicates = 0
        merged_count = 0

        for subdomain, count in duplicates:
            try:
                # Get all domains with this subdomain
                domains = Domain.query.filter_by(subdomain=subdomain).all()

                if len(domains) > 1:
                    # Keep the first domain and merge others into it
                    primary_domain = domains[0]

                    # Merge tags and sources from all domains
                    all_tags = set()
                    all_sources = set()

                    for domain in domains:
                        if domain.tags:
                            all_tags.update(domain.tags.split(","))
                        all_sources.add(domain.source)

                    # Update primary domain
                    primary_domain.tags = ",".join(filter(None, all_tags))
                    primary_domain.source = ",".join(all_sources)
                    primary_domain.updated_at = datetime.utcnow()

                    # Delete duplicate domains
                    for domain in domains[1:]:
                        db.session.delete(domain)

                    merged_count += len(domains) - 1

                processed_duplicates += 1

                # Update progress
                progress = int((processed_duplicates / total_duplicates) * 100)
                job.progress = progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": processed_duplicates,
                        "total": total_duplicates,
                        "merged": merged_count,
                        "progress": progress,
                    },
                )

                # Commit periodically
                if processed_duplicates % 50 == 0:
                    db.session.commit()

            except Exception as e:
                print(f"Error deduplicating domain {subdomain}: {e}")
                processed_duplicates += 1

        # Final commit
        db.session.commit()

        # Update job with final results
        job.status = "completed"
        job.progress = 100
        job.result = json.dumps(
            {
                "total_processed": processed_duplicates,
                "merged_count": merged_count,
                "completion_time": datetime.utcnow().isoformat(),
            }
        )
        db.session.commit()

        return {
            "status": "completed",
            "total_processed": processed_duplicates,
            "merged_count": merged_count,
        }

    except Exception as e:
        # Update job with error
        if job_id:
            job = Job.query.get(job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.session.commit()
        raise


@celery_app.task(bind=True, name="cleanup_old_domains")
def cleanup_old_domains_task(self, days_old=30, job_id=None):
    """
    Background task for cleaning up old domain records

    Args:
        days_old: Number of days to keep domains
        job_id: Optional job ID to track progress
    """

    try:
        from datetime import timedelta

        # Get or create job record
        if job_id:
            job = Job.query.get(job_id)
            if not job:
                job = Job(type="data_cleanup", status="running", progress=0)
                db.session.add(job)
                db.session.commit()
        else:
            job = Job(type="data_cleanup", status="running", progress=0)
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Find old domains
        old_domains = Domain.query.filter(Domain.created_at < cutoff_date).all()

        total_domains = len(old_domains)
        processed_domains = 0
        deleted_count = 0

        for domain in old_domains:
            try:
                db.session.delete(domain)
                deleted_count += 1
                processed_domains += 1

                # Update progress
                progress = int((processed_domains / total_domains) * 100)
                job.progress = progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": processed_domains,
                        "total": total_domains,
                        "deleted": deleted_count,
                        "progress": progress,
                    },
                )

                # Commit periodically
                if processed_domains % 100 == 0:
                    db.session.commit()

            except Exception as e:
                print(f"Error deleting domain {domain.subdomain}: {e}")
                processed_domains += 1

        # Final commit
        db.session.commit()

        # Update job with final results
        job.status = "completed"
        job.progress = 100
        job.result = json.dumps(
            {
                "total_processed": processed_domains,
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "completion_time": datetime.utcnow().isoformat(),
            }
        )
        db.session.commit()

        return {
            "status": "completed",
            "total_processed": processed_domains,
            "deleted_count": deleted_count,
        }

    except Exception as e:
        # Update job with error
        if job_id:
            job = Job.query.get(job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                db.session.commit()
        raise


def _normalize_domain(domain):
    """
    Normalize a domain name

    Args:
        domain: Domain name to normalize

    Returns:
        Normalized domain name
    """

    if not domain:
        return domain

    # Convert to lowercase
    domain = domain.lower()

    # Remove trailing dot
    if domain.endswith("."):
        domain = domain[:-1]

    # Remove www prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    # Remove common prefixes that might be noise
    noise_prefixes = ["m.", "mobile.", "wap."]
    for prefix in noise_prefixes:
        if domain.startswith(prefix):
            domain = domain[len(prefix) :]
            break

    # Basic validation
    if not domain or "." not in domain:
        return domain

    # Remove extra whitespace
    domain = domain.strip()

    return domain
