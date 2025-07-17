"""
Domain enumeration service
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from app import db
from app.models.models import Job, Domain, APIKey
from app.services.external_apis import CertificateTransparencyAPI, VirusTotalAPI, ShodanAPI


class EnumerationService:
    """Service for managing domain enumeration jobs"""
    
    def __init__(self):
        self.supported_sources = {
            'crt.sh': CertificateTransparencyAPI(),
            'virustotal': VirusTotalAPI(),
            'shodan': ShodanAPI()
        }
    
    def start_enumeration(self, domains, sources, options):
        """Start a new enumeration job"""
        # Create job record
        job = Job(
            type='domain_enumeration',
            domain=','.join(domains),
            status='pending',
            progress=0
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start background task
        self._start_background_enumeration(job.id, domains, sources, options)
        
        return job
    
    def _start_background_enumeration(self, job_id, domains, sources, options):
        """Start background enumeration task"""
        # In a real application, this would use Celery or similar
        # For now, we'll simulate with a simple async task
        import threading
        
        def run_enumeration():
            asyncio.run(self._run_enumeration(job_id, domains, sources, options))
        
        thread = threading.Thread(target=run_enumeration)
        thread.daemon = True
        thread.start()
    
    async def _run_enumeration(self, job_id, domains, sources, options):
        """Run the actual enumeration"""
        job = Job.query.get(job_id)
        if not job:
            return
        
        try:
            job.status = 'running'
            db.session.commit()
            
            total_domains = len(domains)
            total_sources = len(sources)
            total_tasks = total_domains * total_sources
            completed_tasks = 0
            
            all_results = []
            
            for domain in domains:
                for source in sources:
                    try:
                        # Update progress
                        progress = int((completed_tasks / total_tasks) * 100)
                        job.progress = progress
                        db.session.commit()
                        
                        # Run enumeration for this domain and source
                        if source in self.supported_sources:
                            api = self.supported_sources[source]
                            
                            # Get API key if needed
                            api_key = None
                            if source in ['virustotal', 'shodan']:
                                key_record = APIKey.query.filter_by(service=source).first()
                                if key_record:
                                    api_key = key_record.key_value
                            
                            # Run enumeration
                            results = await api.enumerate_domain(domain, api_key)
                            
                            # Store results
                            for subdomain in results:
                                existing = Domain.query.filter_by(
                                    subdomain=subdomain,
                                    source=source
                                ).first()
                                
                                if not existing:
                                    domain_record = Domain(
                                        root_domain=domain,
                                        subdomain=subdomain,
                                        source=source,
                                        fetched_at=datetime.utcnow()
                                    )
                                    db.session.add(domain_record)
                                    all_results.append(subdomain)
                        
                        completed_tasks += 1
                        
                    except Exception as e:
                        # Log error but continue with other tasks
                        print(f"Error enumerating {domain} from {source}: {e}")
                        completed_tasks += 1
            
            # Commit all results
            db.session.commit()
            
            # Update job status
            job.status = 'completed'
            job.progress = 100
            job.result = json.dumps({
                'total_found': len(all_results),
                'domains_found': all_results[:100]  # Limit for storage
            })
            db.session.commit()
            
        except Exception as e:
            # Job failed
            job.status = 'failed'
            job.error_message = str(e)
            db.session.commit()
    
    def get_job_status(self, job_id):
        """Get job status"""
        job = Job.query.get(job_id)
        if not job:
            return None
        
        return {
            'id': job.id,
            'status': job.status,
            'progress': job.progress,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None
        }
    
    def cancel_job(self, job_id):
        """Cancel a running job"""
        job = Job.query.get(job_id)
        if not job:
            return False
        
        if job.status in ['pending', 'running']:
            job.status = 'cancelled'
            db.session.commit()
            return True
        
        return False