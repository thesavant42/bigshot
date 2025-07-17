"""
LLM service for OpenAI-compatible API integration
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Iterator, Union
from datetime import datetime

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion

from config.config import Config
from app.models.models import Domain, URL, Job, APIKey
from app import db

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM interactions and chat functionality"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with configuration"""
        try:
            api_key = self.config.OPENAI_API_KEY
            if not api_key:
                # Try to get from database (only if in app context)
                try:
                    from flask import has_app_context
                    if has_app_context():
                        api_key_record = APIKey.query.filter_by(service='openai', is_active=True).first()
                        if api_key_record:
                            api_key = api_key_record.key_value
                except ImportError:
                    pass
            
            if not api_key:
                logger.warning("No OpenAI API key configured")
                return
                
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.config.OPENAI_API_BASE
            )
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.client is not None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.client:
            return []
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Generate response from LLM"""
        if not self.client:
            raise RuntimeError("LLM client not available")
        
        model = model or self.config.OPENAI_MODEL
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                stream=stream,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            raise
    
    def create_chat_completion(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Create chat completion with context"""
        if not self.client:
            raise RuntimeError("LLM client not available")
        
        # Build messages list
        messages = []
        
        # Add system message with context
        system_message = self._build_system_message(context)
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Get MCP tools if available
        tools = self._get_mcp_tools()
        
        try:
            response = self.generate_response(
                messages=messages,
                tools=tools,
                stream=stream
            )
            
            if stream:
                return self._process_streaming_response(response)
            else:
                return self._process_response(response)
        except Exception as e:
            logger.error(f"Failed to create chat completion: {e}")
            raise
    
    def _build_system_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system message with context"""
        system_message = """You are an AI assistant helping with cybersecurity reconnaissance and bug bounty research. 
        You have access to a database of discovered domains, URLs, and reconnaissance job information.
        
        You can help with:
        - Analyzing discovered domains and subdomains
        - Providing information about targets
        - Suggesting reconnaissance strategies
        - Enriching data with external information
        
        Use the available tools to query the database and provide accurate, helpful information."""
        
        if context:
            system_message += f"\n\nCurrent context:\n{json.dumps(context, indent=2)}"
        
        return system_message
    
    def _get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "query_domains",
                    "description": "Query domains from the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "root_domain": {
                                "type": "string",
                                "description": "Root domain to filter by"
                            },
                            "source": {
                                "type": "string",
                                "description": "Source to filter by (e.g., crt.sh, virustotal)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_urls",
                    "description": "Query URLs from the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain to filter by"
                            },
                            "status_code": {
                                "type": "integer",
                                "description": "HTTP status code to filter by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_jobs",
                    "description": "Query reconnaissance jobs from the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Job status to filter by"
                            },
                            "job_type": {
                                "type": "string",
                                "description": "Job type to filter by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 20
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_wikipedia_info",
                    "description": "Get information about a topic from Wikipedia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for Wikipedia"
                            },
                            "sentences": {
                                "type": "integer",
                                "description": "Number of sentences to return",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        return tools
    
    def _process_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Process non-streaming response"""
        message = response.choices[0].message
        
        result = {
            "content": message.content,
            "role": message.role,
            "function_calls": [],
            "usage": response.usage.model_dump() if response.usage else None
        }
        
        # Handle function calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_call = {
                    "id": tool_call.id,
                    "function": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "result": None
                }
                
                # Execute function call
                try:
                    function_result = self._execute_function_call(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )
                    function_call["result"] = function_result
                except Exception as e:
                    logger.error(f"Failed to execute function call: {e}")
                    function_call["result"] = {"error": str(e)}
                
                result["function_calls"].append(function_call)
        
        return result
    
    def _process_streaming_response(self, response: Iterator[ChatCompletionChunk]) -> Iterator[Dict[str, Any]]:
        """Process streaming response"""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                yield {
                    "content": delta.content,
                    "role": delta.role,
                    "finish_reason": chunk.choices[0].finish_reason,
                    "usage": chunk.usage.model_dump() if chunk.usage else None
                }
    
    def _execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP function call"""
        try:
            if function_name == "query_domains":
                return self._query_domains(**arguments)
            elif function_name == "query_urls":
                return self._query_urls(**arguments)
            elif function_name == "query_jobs":
                return self._query_jobs(**arguments)
            elif function_name == "get_wikipedia_info":
                return self._get_wikipedia_info(**arguments)
            else:
                raise ValueError(f"Unknown function: {function_name}")
        except Exception as e:
            logger.error(f"Function call {function_name} failed: {e}")
            raise
    
    def _query_domains(self, root_domain: str = None, source: str = None, limit: int = 50) -> Dict[str, Any]:
        """Query domains from database"""
        query = Domain.query
        
        if root_domain:
            query = query.filter(Domain.root_domain == root_domain)
        if source:
            query = query.filter(Domain.source == source)
        
        domains = query.limit(limit).all()
        
        return {
            "domains": [domain.to_dict() for domain in domains],
            "total": len(domains)
        }
    
    def _query_urls(self, domain: str = None, status_code: int = None, limit: int = 50) -> Dict[str, Any]:
        """Query URLs from database"""
        query = URL.query
        
        if domain:
            query = query.filter(URL.domain == domain)
        if status_code:
            query = query.filter(URL.status_code == status_code)
        
        urls = query.limit(limit).all()
        
        return {
            "urls": [url.to_dict() for url in urls],
            "total": len(urls)
        }
    
    def _query_jobs(self, status: str = None, job_type: str = None, limit: int = 20) -> Dict[str, Any]:
        """Query jobs from database"""
        query = Job.query
        
        if status:
            query = query.filter(Job.status == status)
        if job_type:
            query = query.filter(Job.type == job_type)
        
        jobs = query.limit(limit).all()
        
        return {
            "jobs": [job.to_dict() for job in jobs],
            "total": len(jobs)
        }
    
    def _get_wikipedia_info(self, query: str, sentences: int = 3) -> Dict[str, Any]:
        """Get information from Wikipedia"""
        try:
            import wikipedia
            
            # Search for the page
            search_results = wikipedia.search(query, results=5)
            if not search_results:
                return {"error": "No Wikipedia pages found for the query"}
            
            # Get the first result
            page_title = search_results[0]
            page = wikipedia.page(page_title)
            
            # Get summary
            summary = wikipedia.summary(page_title, sentences=sentences)
            
            return {
                "title": page.title,
                "summary": summary,
                "url": page.url,
                "categories": page.categories[:10] if page.categories else [],
                "links": page.links[:10] if page.links else []
            }
        except wikipedia.exceptions.DisambiguationError as e:
            # Try the first option
            try:
                page = wikipedia.page(e.options[0])
                summary = wikipedia.summary(e.options[0], sentences=sentences)
                return {
                    "title": page.title,
                    "summary": summary,
                    "url": page.url,
                    "categories": page.categories[:10] if page.categories else [],
                    "links": page.links[:10] if page.links else []
                }
            except Exception:
                return {"error": f"Multiple pages found: {e.options[:5]}"}
        except Exception as e:
            logger.error(f"Wikipedia query failed: {e}")
            return {"error": str(e)}


# Global LLM service instance
llm_service = LLMService()