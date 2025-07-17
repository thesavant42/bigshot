"""
External API integrations for domain enumeration
"""

import aiohttp
import json
import asyncio
from urllib.parse import quote


class CertificateTransparencyAPI:
    """Certificate Transparency (crt.sh) API integration"""

    def __init__(self):
        self.base_url = "https://crt.sh"

    async def enumerate_domain(self, domain, api_key=None):
        """Enumerate subdomains using Certificate Transparency logs"""
        try:
            url = f"{self.base_url}/?q=%.{domain}&output=json"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract unique subdomains
                        subdomains = set()
                        for entry in data:
                            if "name_value" in entry:
                                names = entry["name_value"].split("\n")
                                for name in names:
                                    name = name.strip()
                                    if name and name.endswith(f".{domain}"):
                                        subdomains.add(name)

                        return list(subdomains)
                    else:
                        print(f"crt.sh API returned status {response.status}")
                        return []

        except Exception as e:
            print(f"Error with crt.sh API: {e}")
            return []


class VirusTotalAPI:
    """VirusTotal API integration"""

    def __init__(self):
        self.base_url = "https://www.virustotal.com/vtapi/v2"

    async def enumerate_domain(self, domain, api_key):
        """Enumerate subdomains using VirusTotal API"""
        if not api_key:
            print("VirusTotal API key not configured")
            return []

        try:
            url = f"{self.base_url}/domain/report"
            params = {"apikey": api_key, "domain": domain}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract subdomains from various fields
                        subdomains = set()

                        # From subdomains field
                        if "subdomains" in data:
                            for subdomain in data["subdomains"]:
                                if subdomain.endswith(f".{domain}"):
                                    subdomains.add(subdomain)

                        # From detected_urls
                        if "detected_urls" in data:
                            for url_info in data["detected_urls"]:
                                url = url_info.get("url", "")
                                if url:
                                    # Extract domain from URL
                                    try:
                                        from urllib.parse import urlparse

                                        parsed = urlparse(url)
                                        hostname = parsed.hostname
                                        if hostname and hostname.endswith(f".{domain}"):
                                            subdomains.add(hostname)
                                    except:
                                        pass

                        return list(subdomains)
                    else:
                        print(f"VirusTotal API returned status {response.status}")
                        return []

        except Exception as e:
            print(f"Error with VirusTotal API: {e}")
            return []


class ShodanAPI:
    """Shodan API integration"""

    def __init__(self):
        self.base_url = "https://api.shodan.io"

    async def enumerate_domain(self, domain, api_key):
        """Enumerate subdomains using Shodan API"""
        if not api_key:
            print("Shodan API key not configured")
            return []

        try:
            # Search for hosts related to the domain
            url = f"{self.base_url}/shodan/host/search"
            params = {
                "key": api_key,
                "query": f"hostname:*.{domain}",
                "facets": "hostname",
                "minify": True,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract subdomains from matches
                        subdomains = set()

                        if "matches" in data:
                            for match in data["matches"]:
                                if "hostnames" in match:
                                    for hostname in match["hostnames"]:
                                        if hostname.endswith(f".{domain}"):
                                            subdomains.add(hostname)

                        return list(subdomains)
                    else:
                        print(f"Shodan API returned status {response.status}")
                        return []

        except Exception as e:
            print(f"Error with Shodan API: {e}")
            return []


class APIValidator:
    """Utility class for validating API keys"""

    def __init__(self):
        self.apis = {
            "crt.sh": CertificateTransparencyAPI(),
            "virustotal": VirusTotalAPI(),
            "shodan": ShodanAPI(),
        }

    def validate_key(self, service, key):
        """Validate if an API key is properly formatted"""
        if service == "crt.sh":
            return True  # crt.sh doesn't require API key
        elif service == "virustotal":
            return len(key) == 64  # VirusTotal keys are 64 chars
        elif service == "shodan":
            return len(key) == 32  # Shodan keys are 32 chars
        else:
            return False

    async def test_key(self, service, key):
        """Test if an API key is working"""
        if service not in self.apis:
            return {"valid": False, "error": "Unsupported service"}

        try:
            # Test with a known domain
            test_domain = "example.com"
            api = self.apis[service]

            # Run a limited test
            if service == "crt.sh":
                result = await api.enumerate_domain(test_domain)
                return {"valid": True, "domains_found": len(result)}
            else:
                result = await api.enumerate_domain(test_domain, key)
                return {"valid": True, "domains_found": len(result)}

        except Exception as e:
            return {"valid": False, "error": str(e)}
