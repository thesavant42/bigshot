"""
Domain enumeration tasks for background processing
"""

import asyncio
import json
from datetime import datetime
from celery import current_task
from celery_app import celery_app
from app import db
from app.models.models import Job, Domain, APIKey
from app.services.external_apis import (
    CertificateTransparencyAPI,
    VirusTotalAPI,
    ShodanAPI,
)


@celery_app.task(bind=True, name="enumerate_domains")
def enumerate_domains_task(self, job_id, domains, sources, options):
    """
    Background task for domain enumeration

    Args:
        job_id: The ID of the job to update
        domains: List of root domains to enumerate
        sources: List of sources to use for enumeration
        options: Additional options for enumeration
    """

    try:
        # Get job record
        job = Job.query.get(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")

        # Update job status
        job.status = "running"
        job.progress = 0
        db.session.commit()

        # Initialize APIs
        supported_sources = {
            "crt.sh": CertificateTransparencyAPI(),
            "virustotal": VirusTotalAPI(),
            "shodan": ShodanAPI(),
        }

        total_domains = len(domains)
        total_sources = len(sources)
        total_tasks = total_domains * total_sources
        completed_tasks = 0

        all_results = []

        # Run enumeration for each domain and source
        for domain in domains:
            for source in sources:
                try:
                    # Update progress
                    progress = int((completed_tasks / total_tasks) * 100)
                    job.progress = progress
                    current_task.update_state(
                        state="PROGRESS",
                        meta={
                            "current": completed_tasks,
                            "total": total_tasks,
                            "domain": domain,
                            "source": source,
                            "progress": progress,
                        },
                    )
                    db.session.commit()

                    # Broadcast progress update
                    from app.tasks.notifications import broadcast_job_update_task

                    broadcast_job_update_task.delay(
                        job_id,
                        "progress",
                        {
                            "current": completed_tasks,
                            "total": total_tasks,
                            "current_domain": domain,
                            "current_source": source,
                        },
                    )

                    # Run enumeration for this domain and source
                    if source in supported_sources:
                        api = supported_sources[source]

                        # Get API key if needed
                        api_key = None
                        if source in ["virustotal", "shodan"]:
                            key_record = APIKey.query.filter_by(service=source).first()
                            if key_record:
                                api_key = key_record.key_value

                        # Run enumeration (convert async to sync)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            results = loop.run_until_complete(
                                api.enumerate_domain(domain, api_key)
                            )
                        finally:
                            loop.close()

                        # Process and store results
                        for subdomain in results:
                            # Check for existing domain
                            existing = Domain.query.filter_by(
                                subdomain=subdomain, source=source
                            ).first()

                            if not existing:
                                # Create new domain record
                                domain_record = Domain(
                                    root_domain=domain,
                                    subdomain=subdomain,
                                    source=source,
                                    fetched_at=datetime.utcnow(),
                                )
                                db.session.add(domain_record)
                                all_results.append(
                                    {
                                        "subdomain": subdomain,
                                        "source": source,
                                        "root_domain": domain,
                                    }
                                )
                            else:
                                # Update existing record
                                existing.fetched_at = datetime.utcnow()
                                all_results.append(
                                    {
                                        "subdomain": subdomain,
                                        "source": source,
                                        "root_domain": domain,
                                        "existing": True,
                                    }
                                )

                    completed_tasks += 1

                except Exception as e:
                    # Log error but continue with other tasks
                    print(f"Error enumerating {domain} from {source}: {e}")
                    completed_tasks += 1

        # Commit all results
        db.session.commit()

        # Update job with final results
        job.status = "completed"
        job.progress = 100
        job.result = json.dumps(
            {
                "total_found": len(all_results),
                "new_domains": len([r for r in all_results if not r.get("existing")]),
                "updated_domains": len([r for r in all_results if r.get("existing")]),
                "domains_found": all_results[:100],  # Limit for storage
            }
        )
        db.session.commit()

        # Broadcast completion
        from app.tasks.notifications import (
            broadcast_job_update_task,
            send_job_notification_task,
        )

        broadcast_job_update_task.delay(
            job_id,
            "completed",
            {
                "total_found": len(all_results),
                "new_domains": len([r for r in all_results if not r.get("existing")]),
                "updated_domains": len([r for r in all_results if r.get("existing")]),
            },
        )
        send_job_notification_task.delay(job_id, "completed")

        return {
            "status": "completed",
            "total_found": len(all_results),
            "new_domains": len([r for r in all_results if not r.get("existing")]),
            "updated_domains": len([r for r in all_results if r.get("existing")]),
        }

    except Exception as e:
        # Update job with error
        job = Job.query.get(job_id)
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.session.commit()

        # Broadcast failure
        from app.tasks.notifications import (
            broadcast_job_update_task,
            send_job_notification_task,
        )

        broadcast_job_update_task.delay(job_id, "failed", {"error_message": str(e)})
        send_job_notification_task.delay(job_id, "failed")

        # Re-raise the exception
        raise


@celery_app.task(bind=True, name="enumerate_single_domain")
def enumerate_single_domain_task(self, domain, source, api_key=None):
    """
    Task for enumerating a single domain from a single source

    Args:
        domain: The domain to enumerate
        source: The source to use (crt.sh, virustotal, shodan)
        api_key: Optional API key for the source

    Returns:
        List of subdomains found
    """

    try:
        # Initialize API
        supported_sources = {
            "crt.sh": CertificateTransparencyAPI(),
            "virustotal": VirusTotalAPI(),
            "shodan": ShodanAPI(),
        }

        if source not in supported_sources:
            raise Exception(f"Unsupported source: {source}")

        api = supported_sources[source]

        # Get API key from database if not provided
        if not api_key and source in ["virustotal", "shodan"]:
            key_record = APIKey.query.filter_by(service=source).first()
            if key_record:
                api_key = key_record.key_value

        # Run enumeration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(api.enumerate_domain(domain, api_key))
        finally:
            loop.close()

        return {
            "domain": domain,
            "source": source,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        # Log error and return empty results
        print(f"Error enumerating {domain} from {source}: {e}")
        return {
            "domain": domain,
            "source": source,
            "results": [],
            "count": 0,
            "error": str(e),
        }


@celery_app.task(bind=True, name="cancel_enumeration")
def cancel_enumeration_task(self, job_id):
    """
    Cancel an enumeration job

    Args:
        job_id: The ID of the job to cancel
    """

    try:
        job = Job.query.get(job_id)
        if not job:
            return False

        # Update job status
        job.status = "cancelled"
        job.error_message = "Job cancelled by user"
        db.session.commit()

        # Revoke the task if it's still running
        celery_app.control.revoke(self.request.id, terminate=True)

        return True

    except Exception as e:
        print(f"Error cancelling job {job_id}: {e}")
        return False
