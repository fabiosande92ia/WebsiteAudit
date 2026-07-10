import pytest
from unittest.mock import AsyncMock, patch

from app.services.security_service import run_security_checks
from app.services.lighthouse_service import extract_lighthouse_metrics

@pytest.mark.asyncio
async def test_run_security_checks_https(mocker):
    # Mock httpx response to avoid real network calls
    mock_response = mocker.Mock()
    mock_response.headers = {
        "strict-transport-security": "max-age=31536000",
        "content-security-policy": "default-src 'self'",
        "x-frame-options": "SAMEORIGIN",
        "x-content-type-options": "nosniff"
    }

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    results = await run_security_checks("https://example.com")

    assert results["https_active"] == True
    assert results["hsts_active"] == True
    assert results["csp_active"] == True
    assert results["x_frame_options_active"] == True
    assert results["x_content_type_options_active"] == True

def test_extract_lighthouse_metrics():
    mock_data = {
        "categories": {
            "performance": {"score": 0.95},
            "accessibility": {"score": 1.0},
            "best-practices": {"score": 0.8},
            "seo": {"score": 0.9}
        },
        "audits": {
            "first-contentful-paint": {"numericValue": 1000},
            "largest-contentful-paint": {"numericValue": 2500},
            "cumulative-layout-shift": {"numericValue": 0.05}
        }
    }

    metrics = extract_lighthouse_metrics(mock_data)

    assert metrics["performance"] == 95.0
    assert metrics["accessibility"] == 100.0
    assert metrics["best_practices"] == 80.0
    assert metrics["seo"] == 90.0
    assert metrics["first_contentful_paint"] == 1000
    assert metrics["largest_contentful_paint"] == 2500
    assert metrics["cumulative_layout_shift"] == 0.05
