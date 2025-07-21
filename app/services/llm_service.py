"""
LLM service for OpenAI-compatible API integration
"""

import json
import logging
import os
import time
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
        self.current_provider_config = None
        self.provider = self.config.LLM_PROVIDER.lower()
        self._initialize_client()

    def _initialize_client(self):
        """Initialize LLM client based on configured provider"""
        try:
            # Try to load active provider from database first
            if self._load_active_provider_from_db():
                return

            # Fall back to config-based initialization
            if self.provider == "lmstudio":
                self._initialize_lmstudio_client()
            else:
                self._initialize_openai_client()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None

    def _load_active_provider_from_db(self):
        """Load active provider configuration from database"""
        try:
            from flask import has_app_context

            if not has_app_context():
                return False

            from app.models.models import LLMProviderConfig

            active_provider = LLMProviderConfig.query.filter_by(is_active=True).first()

            if active_provider:
                # Ensure the provider is attached to the session
                active_provider = db.session.merge(active_provider)
                self._initialize_client_from_config(active_provider)
                return True
            return False
        except Exception as e:
            logger.warning(f"Could not load provider from database: {e}")
            return False

    def _initialize_client_from_config(self, provider_config):
        """Initialize client from a provider configuration"""
        try:
            # Attach to session to prevent detached instance errors
            provider_config = db.session.merge(provider_config)
            self.current_provider_config = provider_config
            self.provider = provider_config.provider.lower()

            # Use the provider config for initialization
            api_key = provider_config.api_key or "dummy-key"
            if provider_config.provider.lower() == "lmstudio":
                api_key = api_key or "lm-studio"

            self.client = OpenAI(
                api_key=api_key,
                base_url=provider_config.base_url,
                timeout=provider_config.connection_timeout,
            )

            logger.info(f"LLM client initialized with provider: {provider_config.name}")

        except Exception as e:
            # Handle detached instance and other errors
            import sqlalchemy

            if isinstance(e, sqlalchemy.orm.exc.DetachedInstanceError):
                logger.error(f"ProviderConfig is detached: {e}")
            else:
                logger.error(f"Failed to initialize client from config: {e}")
            self.client = None
            self.current_provider_config = None

    def _initialize_openai_client(self):
        """Initialize OpenAI client with configuration"""
        api_key = self.config.OPENAI_API_KEY
        if not api_key:
            # Try to get from database (only if in app context)
            try:
                from flask import has_app_context

                if has_app_context():
                    api_key_record = APIKey.query.filter_by(
                        service="openai", is_active=True
                    ).first()
                    if api_key_record:
                        api_key = api_key_record.key_value
            except ImportError:
                pass

        if not api_key:
            logger.warning("No OpenAI API key configured")
            return

        self.client = OpenAI(api_key=api_key, base_url=self.config.OPENAI_API_BASE)
        logger.info("OpenAI client initialized successfully")

    def _initialize_lmstudio_client(self):
        """Initialize LMStudio client using OpenAI-compatible API"""
        # LMStudio uses a dummy API key by default
        api_key = self.config.LMSTUDIO_API_KEY or "lm-studio"
        base_url = self.config.LMSTUDIO_API_BASE

        # Check if LMStudio server is accessible (optional check)
        try:
            import requests

            response = requests.get(f"{base_url.rstrip('/v1')}/v1/models", timeout=5)
            if response.status_code != 200:
                logger.warning(f"LMStudio server may not be accessible at {base_url}")
        except Exception as e:
            logger.warning(f"Could not verify LMStudio server accessibility: {e}")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        logger.info(f"LMStudio client initialized successfully at {base_url}")

    def get_current_provider(self) -> str:
        """Get the current LLM provider"""
        return self.provider

    def get_default_model(self) -> str:
        """Get the default model for the current provider"""
        if self.current_provider_config:
            try:
                # Ensure the provider config is attached to session
                provider_config = db.session.merge(self.current_provider_config)
                return provider_config.model
            except Exception as e:
                logger.warning(f"Could not access provider config model: {e}")
                # Fall back to config-based model
                pass

        # Return provider-specific default model regardless of client state (supports testing scenarios)
        if self.provider == "lmstudio":
            return self.config.LMSTUDIO_MODEL
        else:
            return self.config.OPENAI_MODEL

    def get_current_provider_info(self) -> dict:
        """Get information about the current provider"""
        if self.current_provider_config:
            try:
                # Ensure the provider config is attached to session
                provider_config = db.session.merge(self.current_provider_config)
                return {
                    "id": provider_config.id,
                    "name": provider_config.name,
                    "provider": provider_config.provider,
                    "base_url": provider_config.base_url,
                    "model": provider_config.model,
                    "source": "database",
                }
            except Exception as e:
                logger.warning(f"Could not access provider config info: {e}")
                # Fall back to legacy info
                pass

        return {
            "name": f"{self.provider.upper()} (Legacy)",
            "provider": self.provider,
            "base_url": self._get_legacy_base_url(),
            "model": self.get_default_model(),
            "source": "config",
        }

    def _get_legacy_base_url(self) -> str:
        """Get base URL for legacy configuration"""
        if self.provider == "lmstudio":
            return self.config.LMSTUDIO_API_BASE
        else:
            return self.config.OPENAI_API_BASE

    def switch_provider(self, provider_config):
        """Switch to a different provider configuration at runtime"""
        try:
            old_provider = self.get_current_provider_info()
            self._initialize_client_from_config(provider_config)

            if self.client:
                logger.info(
                    f"Successfully switched from {old_provider.get('name')} to {provider_config.name}"
                )
                return True
            else:
                logger.error(f"Failed to switch to provider {provider_config.name}")
                return False
        except Exception as e:
            logger.error(f"Error switching provider: {e}")
            return False

    def test_provider_connection(self, provider_config):
        """Test connection to a provider without switching the active client"""
        try:
            # Create a temporary client for testing
            api_key = provider_config.api_key or "dummy-key"
            if provider_config.provider.lower() == "lmstudio":
                api_key = api_key or "lm-studio"

            test_client = OpenAI(
                api_key=api_key,
                base_url=provider_config.base_url,
                timeout=provider_config.connection_timeout,
            )

            # Test with a simple request
            start_time = datetime.now()

            # Try to list models first
            try:
                models = test_client.models.list()
                model_list = [model.id for model in models.data]
                if not model_list:
                    model_list = [provider_config.model]  # Fallback to configured model
            except Exception:
                model_list = [
                    provider_config.model
                ]  # Fallback if models endpoint fails

            # Test a simple completion
            test_response = test_client.chat.completions.create(
                model=provider_config.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, this is a connection test. Please respond with 'OK'.",
                    }
                ],
                max_tokens=10,
                timeout=10,
            )

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            # Safely extract response content
            test_content = "No response"
            if (
                test_response
                and test_response.choices
                and len(test_response.choices) > 0
            ):
                if (
                    test_response.choices[0].message
                    and test_response.choices[0].message.content
                ):
                    test_content = test_response.choices[0].message.content.strip()

            result = {
                "success": True,
                "response_time": response_time,
                "models_available": model_list,
                "test_response": test_content,
                "provider_info": {
                    "name": provider_config.name,
                    "provider": provider_config.provider,
                    "base_url": provider_config.base_url,
                    "model": provider_config.model,
                },
                "timestamp": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider_info": {
                    "name": provider_config.name,
                    "provider": provider_config.provider,
                    "base_url": provider_config.base_url,
                    "model": provider_config.model,
                },
                "timestamp": datetime.now().isoformat(),
            }

    def is_available(self) -> bool:
        """Check if LLM service is available"""
        # Check if we have a client object (does not verify functionality)
        if self.client is not None:
            return True
        
        # If mock mode is enabled, consider it available
        if self.config.LLM_MOCK_MODE:
            return True
            
        # Otherwise, not available
        return False

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.client:
            # Only return mock models if mock mode is enabled
            if self.config.LLM_MOCK_MODE:
                return ["mock-model", "bigshot-assistant"]
            else:
                return []

        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            # Only return mock models on error if mock mode is enabled
            if self.config.LLM_MOCK_MODE:
                return ["mock-model", "bigshot-assistant"]
            else:
                return []

    def get_detailed_models(self) -> List[Dict[str, Any]]:
        """Get detailed list of available models with metadata"""
        if not self.client:
            return []

        try:
            models = self.client.models.list()
            detailed_models = []
            for model in models.data:
                model_info = {
                    "id": model.id,
                    "object": model.object,
                    "created": getattr(model, "created", None),
                    "owned_by": getattr(model, "owned_by", "lmstudio"),
                }

                # Add LM Studio specific fields if available
                if hasattr(model, "type"):
                    model_info["type"] = model.type
                if hasattr(model, "arch"):
                    model_info["arch"] = model.arch
                if hasattr(model, "state"):
                    model_info["state"] = model.state
                if hasattr(model, "max_context_length"):
                    model_info["max_context_length"] = model.max_context_length

                detailed_models.append(model_info)

            return detailed_models
        except Exception as e:
            logger.error(f"Failed to get detailed models: {e}")
            return []

    def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Generate response from LLM"""
        if not self.client:
            raise RuntimeError("LLM client not available")

        model = model or self.get_default_model()

        try:
            response = self.client.chat.completions.create(
                model=model, messages=messages, tools=tools, stream=stream, **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            raise

    def create_text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Create text completion using /v1/completions endpoint"""
        if not self.client:
            raise RuntimeError("LLM client not available")

        model = model or self.get_default_model()

        try:
            # Use the completions endpoint instead of chat completions
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                stop=stop,
                **kwargs,
            )

            if stream:
                return self._process_streaming_completion_response(response)
            else:
                return self._process_completion_response(response)
        except Exception as e:
            logger.error(f"Failed to create text completion: {e}")
            raise

    def create_embeddings(
        self,
        input_text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create embeddings using /v1/embeddings endpoint"""
        if not self.client:
            raise RuntimeError("LLM client not available")

        # Use embedding model if available, otherwise use default
        if not model:
            if self.current_provider_config:
                # Look for embedding model in provider config
                model = getattr(self.current_provider_config, "embedding_model", None)
            if not model:
                model = self.get_default_model()

        try:
            response = self.client.embeddings.create(
                input=input_text, model=model, **kwargs
            )

            return {
                "object": response.object,
                "data": [
                    {
                        "object": embedding.object,
                        "embedding": embedding.embedding,
                        "index": embedding.index,
                    }
                    for embedding in response.data
                ],
                "model": response.model,
                "usage": response.usage.model_dump() if response.usage else None,
            }
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise

    def create_chat_completion(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        model: Optional[str] = None,  # Add model parameter
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Create chat completion with context"""
        if not self.client:
            # Only fallback to mock response if mock mode is enabled
            if self.config.LLM_MOCK_MODE:
                return self._create_mock_response(message, context, stream)
            else:
                raise RuntimeError(
                    "LLM client not available. Please configure the LLM_PROVIDER environment variable and ensure the service is running. "
                    "Alternatively, set LLM_MOCK_MODE=true for testing purposes."
                )

        # Build messages list
        messages = []

        # Add system message with context
        system_message = self._build_system_message(context)
        messages.append({"role": "system", "content": system_message})

        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                )

        # Add current message
        messages.append({"role": "user", "content": message})

        # Get MCP tools if available
        tools = self._get_mcp_tools()

        try:
            response = self.generate_response(
                messages=messages,
                tools=tools,
                stream=stream,
                model=model,  # Pass model parameter
            )

            if stream:
                return self._process_streaming_response(response)
            else:
                return self._process_response(response)
        except Exception as e:
            logger.error(f"Failed to create chat completion: {e}")
            # Only fallback to mock response if mock mode is enabled
            if self.config.LLM_MOCK_MODE:
                logger.info("Falling back to mock response due to LLM service error")
                return self._create_mock_response(message, context, stream)
            else:
                raise

    def _build_system_message(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system message with context"""
        system_message = f"""You are an AI assistant helping with cybersecurity reconnaissance and bug bounty research. 
        You have access to a database of discovered domains, URLs, and reconnaissance job information.
        
        Current LLM Provider: {self.get_current_provider().upper()}
        
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
                                "description": "Root domain to filter by",
                            },
                            "source": {
                                "type": "string",
                                "description": "Source to filter by (e.g., crt.sh, virustotal)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50,
                            },
                        },
                    },
                },
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
                                "description": "Domain to filter by",
                            },
                            "status_code": {
                                "type": "integer",
                                "description": "HTTP status code to filter by",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50,
                            },
                        },
                    },
                },
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
                                "description": "Job status to filter by",
                            },
                            "job_type": {
                                "type": "string",
                                "description": "Job type to filter by",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 20,
                            },
                        },
                    },
                },
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
                                "description": "Search query for Wikipedia",
                            },
                            "sentences": {
                                "type": "integer",
                                "description": "Number of sentences to return",
                                "default": 3,
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        return tools

    def _process_completion_response(self, response) -> Dict[str, Any]:
        """Process non-streaming completion response"""
        # Validate response structure
        if not response or not response.choices or len(response.choices) == 0:
            raise RuntimeError("Invalid or empty response from LLM service")
            
        choice = response.choices[0]
        if not choice:
            raise RuntimeError("Invalid choice structure in LLM response")

        result = {
            "id": response.id,
            "object": response.object,
            "created": response.created,
            "model": response.model,
            "content": choice.text or "",
            "finish_reason": choice.finish_reason,
            "usage": response.usage.model_dump() if response.usage else None,
        }

        # Add LM Studio specific stats if available
        if hasattr(response, "stats"):
            result["stats"] = response.stats
        if hasattr(response, "model_info"):
            result["model_info"] = response.model_info

        return result

    def _process_streaming_completion_response(
        self, response
    ) -> Iterator[Dict[str, Any]]:
        """Process streaming completion response"""
        for chunk in response:
            if chunk and chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].text:
                yield {
                    "content": chunk.choices[0].text,
                    "finish_reason": chunk.choices[0].finish_reason,
                    "usage": chunk.usage.model_dump() if chunk.usage else None,
                }

    def _process_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Process non-streaming chat response"""
        # Validate response structure
        if not response or not response.choices or len(response.choices) == 0:
            raise RuntimeError("Invalid or empty response from LLM service")
        
        message = response.choices[0].message
        if not message:
            raise RuntimeError("Invalid message structure in LLM response")

        result = {
            "content": message.content or "",
            "role": message.role or "assistant",
            "function_calls": [],
            "usage": response.usage.model_dump() if response.usage else None,
        }

        # Handle function calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_call = {
                    "id": tool_call.id,
                    "function": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "result": None,
                }

                # Execute function call
                try:
                    function_result = self._execute_function_call(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments),
                    )
                    function_call["result"] = function_result
                except Exception as e:
                    logger.error(f"Failed to execute function call: {e}")
                    function_call["result"] = {"error": str(e)}

                result["function_calls"].append(function_call)

        return result

    def _process_streaming_response(
        self, response: Iterator[ChatCompletionChunk]
    ) -> Iterator[Dict[str, Any]]:
        """Process streaming response"""
        for chunk in response:
            if chunk and chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                yield {
                    "content": delta.content or "",
                    "role": delta.role,
                    "finish_reason": chunk.choices[0].finish_reason,
                    "usage": chunk.usage.model_dump() if chunk.usage else None,
                }

    def _execute_function_call(
        self, function_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def _query_domains(
        self, root_domain: str = None, source: str = None, limit: int = 50
    ) -> Dict[str, Any]:
        """Query domains from database"""
        query = Domain.query

        if root_domain:
            query = query.filter(Domain.root_domain == root_domain)
        if source:
            query = query.filter(Domain.source == source)

        domains = query.limit(limit).all()

        return {
            "domains": [domain.to_dict() for domain in domains],
            "total": len(domains),
        }

    def _query_urls(
        self, domain: str = None, status_code: int = None, limit: int = 50
    ) -> Dict[str, Any]:
        """Query URLs from database"""
        query = URL.query

        if domain:
            query = query.filter(URL.domain == domain)
        if status_code:
            query = query.filter(URL.status_code == status_code)

        urls = query.limit(limit).all()

        return {"urls": [url.to_dict() for url in urls], "total": len(urls)}

    def _query_jobs(
        self, status: str = None, job_type: str = None, limit: int = 20
    ) -> Dict[str, Any]:
        """Query jobs from database"""
        query = Job.query

        if status:
            query = query.filter(Job.status == status)
        if job_type:
            query = query.filter(Job.type == job_type)

        jobs = query.limit(limit).all()

        return {"jobs": [job.to_dict() for job in jobs], "total": len(jobs)}

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
                "links": page.links[:10] if page.links else [],
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
                    "links": page.links[:10] if page.links else [],
                }
            except Exception:
                return {"error": f"Multiple pages found: {e.options[:5]}"}
        except Exception as e:
            logger.error(f"Wikipedia query failed: {e}")
            return {"error": str(e)}

    def _create_mock_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Create a mock response when LLM service is not available"""

        # Generate a helpful mock response based on the message content
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "help"]):
            mock_content = """Hello! I'm a mock AI assistant for BigShot. 

I can help you with domain reconnaissance and security research, but I'm currently running in mock mode because the LLM service isn't available.

To set up a real LLM connection:
1. Configure LMStudio locally and make sure it's running
2. Update the LLM provider settings in the Configuration section
3. Or configure an OpenAI API key for full functionality

For now, I can still help you understand the BigShot interface and features!"""

        elif any(
            word in message_lower for word in ["domain", "subdomain", "enumerate"]
        ):
            mock_content = """I can help with domain reconnaissance! Here are some key features of BigShot:

🔍 **Domain Discovery**: Find subdomains using multiple sources (crt.sh, VirusTotal, etc.)
📊 **Data Analysis**: Organize and analyze discovered domains and URLs  
🚀 **Background Jobs**: Run enumeration tasks asynchronously
💾 **Data Storage**: Store results in a PostgreSQL database

To get started:
1. Click "Add Domain" to start enumerating a target domain
2. Use the filters to organize your results
3. Monitor job progress in the "View Jobs" panel

Note: I'm running in mock mode - enable a real LLM for advanced AI assistance!"""

        elif any(word in message_lower for word in ["config", "setup", "provider"]):
            mock_content = """Here's how to configure the LLM providers:

🔧 **LMStudio Setup**:
1. Install LMStudio on your host machine
2. Download a compatible model (e.g., Llama 3.2)
3. Start the server (usually on localhost:1234)
4. Update the provider URL in Settings → LLM Providers

🤖 **OpenAI Setup**:
1. Get an API key from OpenAI
2. Add it in Settings → LLM Providers
3. Select OpenAI as the active provider

The mock mode you're seeing now is a fallback when no working LLM is configured."""

        else:
            mock_content = f"""I received your message: "{message}"

I'm currently running in mock mode because the LLM service isn't available. This means I can provide basic responses but not full AI functionality.

To enable full AI capabilities:
- Configure LMStudio or OpenAI in the Settings
- Make sure the service is running and accessible
- Check the provider configuration

Would you like help with domain reconnaissance features or LLM configuration?"""

        mock_response = {
            "role": "assistant",
            "content": mock_content,
            "mock": True,
            "timestamp": datetime.now().isoformat(),
        }

        if stream:

            def mock_stream():
                # Simulate streaming by yielding chunks
                words = mock_content.split()
                for i in range(0, len(words), 3):  # Send 3 words at a time
                    chunk_words = words[i : i + 3]
                    chunk_content = " " + " ".join(chunk_words)
                    yield {"type": "content", "content": chunk_content, "mock": True}
                    time.sleep(0.1)  # Small delay to simulate streaming

                yield {"type": "done", "mock": True}

            return mock_stream()
        else:
            return mock_response


# Global LLM service instance
llm_service = LLMService()
