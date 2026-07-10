import httpx
import logging
from typing import Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

async def run_security_checks(url: str) -> Dict[str, bool]:
    """
    Perform basic security checks on the given URL:
    - HTTPS active
    - HSTS
    - Content-Security-Policy
    - X-Frame-Options
    - X-Content-Type-Options
    """
    results = {
        "https_active": False,
        "hsts_active": False,
        "csp_active": False,
        "x_frame_options_active": False,
        "x_content_type_options_active": False
    }

    parsed_url = urlparse(url)
    if parsed_url.scheme == "https":
        results["https_active"] = True
    else:
        # Check if it redirects to HTTPS
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                response = await client.get(url)
                if response.status_code in (301, 302, 307, 308) and response.headers.get("Location", "").startswith("https"):
                    results["https_active"] = True
        except Exception as e:
            logger.warning(f"Error checking HTTPS redirect for {url}: {e}")

    try:
        # Ensure we check the HTTPS version if available for headers
        check_url = url if parsed_url.scheme == "https" else url.replace("http://", "https://", 1)
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(check_url)
            headers = {k.lower(): v for k, v in response.headers.items()}

            if "strict-transport-security" in headers:
                results["hsts_active"] = True

            if "content-security-policy" in headers:
                results["csp_active"] = True

            if "x-frame-options" in headers:
                results["x_frame_options_active"] = True

            if "x-content-type-options" in headers and "nosniff" in headers["x-content-type-options"].lower():
                results["x_content_type_options_active"] = True

    except Exception as e:
        logger.error(f"Error performing security checks for {url}: {e}")

    return results
