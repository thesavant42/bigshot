"""
MCP Server for BigShot application
Provides tools for LLM to interact with the database and external services
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ResourceTemplate,
    Resource,
    GetResourceResult,
)
from app.models.models import Domain, URL, Job, APIKey
from app.services.llm_service import LLMService
from app import create_app, db
from config.config import Config

logger = logging.getLogger(__name__)


class BigShotMCPServer:
    """MCP Server for BigShot application"""

    def __init__(self):
        self.server = Server("bigshot-mcp")
        self.app = create_app()
        self.llm_service = LLMService()
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register MCP tools"""

        @self.server.call_tool()
        async def query_domains(
            root_domain: Optional[str] = None,
            source: Optional[str] = None,
            limit: int = 50,
        ) -> CallToolResult:
            """Query domains from the database"""
            try:
                with self.app.app_context():
                    query = Domain.query

                    if root_domain:
                        query = query.filter(Domain.root_domain == root_domain)
                    if source:
                        query = query.filter(Domain.source == source)

                    domains = query.limit(limit).all()

                    result = {
                        "domains": [domain.to_dict() for domain in domains],
                        "total": len(domains),
                    }

                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result, indent=2))
                        ]
                    )
            except Exception as e:
                logger.error(f"Error querying domains: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

        @self.server.call_tool()
        async def query_urls(
            domain: Optional[str] = None,
            status_code: Optional[int] = None,
            limit: int = 50,
        ) -> CallToolResult:
            """Query URLs from the database"""
            try:
                with self.app.app_context():
                    query = URL.query

                    if domain:
                        query = query.filter(URL.domain == domain)
                    if status_code:
                        query = query.filter(URL.status_code == status_code)

                    urls = query.limit(limit).all()

                    result = {
                        "urls": [url.to_dict() for url in urls],
                        "total": len(urls),
                    }

                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result, indent=2))
                        ]
                    )
            except Exception as e:
                logger.error(f"Error querying URLs: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

        @self.server.call_tool()
        async def query_jobs(
            status: Optional[str] = None,
            job_type: Optional[str] = None,
            limit: int = 20,
        ) -> CallToolResult:
            """Query jobs from the database"""
            try:
                with self.app.app_context():
                    query = Job.query

                    if status:
                        query = query.filter(Job.status == status)
                    if job_type:
                        query = query.filter(Job.type == job_type)

                    jobs = query.limit(limit).all()

                    result = {
                        "jobs": [job.to_dict() for job in jobs],
                        "total": len(jobs),
                    }

                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result, indent=2))
                        ]
                    )
            except Exception as e:
                logger.error(f"Error querying jobs: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

        @self.server.call_tool()
        async def get_wikipedia_info(query: str, sentences: int = 3) -> CallToolResult:
            """Get information from Wikipedia"""
            try:
                result = self.llm_service._get_wikipedia_info(query, sentences)
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )
            except Exception as e:
                logger.error(f"Error getting Wikipedia info: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

        @self.server.call_tool()
        async def get_domain_statistics(
            root_domain: Optional[str] = None,
        ) -> CallToolResult:
            """Get domain statistics"""
            try:
                with self.app.app_context():
                    query = Domain.query

                    if root_domain:
                        query = query.filter(Domain.root_domain == root_domain)

                    total_domains = query.count()

                    # Get count by source
                    source_counts = {}
                    for domain in query.all():
                        source = domain.source
                        source_counts[source] = source_counts.get(source, 0) + 1

                    # Get recent discoveries
                    recent_domains = (
                        query.order_by(Domain.created_at.desc()).limit(10).all()
                    )

                    result = {
                        "total_domains": total_domains,
                        "source_counts": source_counts,
                        "recent_discoveries": [
                            {
                                "subdomain": d.subdomain,
                                "source": d.source,
                                "discovered": (
                                    d.created_at.isoformat() if d.created_at else None
                                ),
                            }
                            for d in recent_domains
                        ],
                    }

                    return CallToolResult(
                        content=[
                            TextContent(type="text", text=json.dumps(result, indent=2))
                        ]
                    )
            except Exception as e:
                logger.error(f"Error getting domain statistics: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    def _register_resources(self):
        """Register MCP resources"""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="domains://all",
                    name="All Domains",
                    description="All discovered domains in the database",
                ),
                Resource(
                    uri="jobs://active",
                    name="Active Jobs",
                    description="Currently running reconnaissance jobs",
                ),
                Resource(
                    uri="statistics://summary",
                    name="Summary Statistics",
                    description="Overall reconnaissance statistics",
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> GetResourceResult:
            """Read a specific resource"""
            try:
                with self.app.app_context():
                    if uri == "domains://all":
                        domains = Domain.query.limit(100).all()
                        content = json.dumps(
                            {
                                "domains": [d.to_dict() for d in domains],
                                "total": len(domains),
                            },
                            indent=2,
                        )

                        return GetResourceResult(
                            contents=[TextContent(type="text", text=content)]
                        )

                    elif uri == "jobs://active":
                        jobs = Job.query.filter_by(status="running").all()
                        content = json.dumps(
                            {"jobs": [j.to_dict() for j in jobs], "total": len(jobs)},
                            indent=2,
                        )

                        return GetResourceResult(
                            contents=[TextContent(type="text", text=content)]
                        )

                    elif uri == "statistics://summary":
                        total_domains = Domain.query.count()
                        total_urls = URL.query.count()
                        total_jobs = Job.query.count()
                        active_jobs = Job.query.filter_by(status="running").count()

                        content = json.dumps(
                            {
                                "total_domains": total_domains,
                                "total_urls": total_urls,
                                "total_jobs": total_jobs,
                                "active_jobs": active_jobs,
                            },
                            indent=2,
                        )

                        return GetResourceResult(
                            contents=[TextContent(type="text", text=content)]
                        )

                    else:
                        return GetResourceResult(
                            contents=[
                                TextContent(
                                    type="text", text=f"Resource not found: {uri}"
                                )
                            ]
                        )
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return GetResourceResult(
                    contents=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    def get_server(self) -> Server:
        """Get the MCP server instance"""
        return self.server


async def main():
    """Main function to run the MCP server"""
    logging.basicConfig(level=logging.INFO)

    mcp_server = BigShotMCPServer()
    server = mcp_server.get_server()

    # Run the server
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1])


if __name__ == "__main__":
    asyncio.run(main())
