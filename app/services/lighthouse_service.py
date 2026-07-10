import asyncio
import json
import os
import tempfile
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def run_lighthouse_audit(url: str) -> Dict[str, Any]:
    """
    Run Lighthouse audit via CLI and parse JSON output.
    Returns a dictionary with extracted metrics.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        command = [
            "lighthouse",
            url,
            "--output=json",
            f"--output-path={output_path}",
            "--quiet",
            "--chrome-flags=--headless --no-sandbox --disable-gpu"
        ]

        logger.info(f"Running lighthouse audit for {url}")

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8')
            logger.error(f"Lighthouse failed for {url}. Error: {error_msg}")
            raise RuntimeError(f"Lighthouse failed: {error_msg}")

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metrics = extract_lighthouse_metrics(data)
        return metrics

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

def extract_lighthouse_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    categories = data.get("categories", {})
    audits = data.get("audits", {})

    metrics = {
        "performance": categories.get("performance", {}).get("score", 0) * 100 if categories.get("performance", {}).get("score") is not None else None,
        "accessibility": categories.get("accessibility", {}).get("score", 0) * 100 if categories.get("accessibility", {}).get("score") is not None else None,
        "best_practices": categories.get("best-practices", {}).get("score", 0) * 100 if categories.get("best-practices", {}).get("score") is not None else None,
        "seo": categories.get("seo", {}).get("score", 0) * 100 if categories.get("seo", {}).get("score") is not None else None,
    }

    # Extract specific audit metrics (values are usually in milliseconds, but numericValue can be used)
    # FCP
    fcp_audit = audits.get("first-contentful-paint", {})
    metrics["first_contentful_paint"] = fcp_audit.get("numericValue")

    # LCP
    lcp_audit = audits.get("largest-contentful-paint", {})
    metrics["largest_contentful_paint"] = lcp_audit.get("numericValue")

    # CLS
    cls_audit = audits.get("cumulative-layout-shift", {})
    metrics["cumulative_layout_shift"] = cls_audit.get("numericValue")

    return metrics
